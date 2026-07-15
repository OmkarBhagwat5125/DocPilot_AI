import os
import shutil
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List

from backend.app.core.auth import get_current_user
from backend.app.core.config import settings
from backend.app.services.document_parser import DocumentParser
from backend.app.services.storage import object_storage
from backend.app.services.embedding import embedding_service
from backend.app.services.vector_db import vector_db
from backend.app.services.chat import chat_service

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# Pydantic models for request/response bodies
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

class DocumentInfo(BaseModel):
    name: str

class UploadResponse(BaseModel):
    filename: str
    chunks_count: int
    message: str

# Allowed extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".csv", ".txt"}

# Document parser instance
parser = DocumentParser()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    filename = file.filename
    ext = Path(filename).suffix.lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}"
        )
        
    # Ensure temporary upload directory exists
    temp_dir = Path(settings.UPLOAD_DIR)
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / f"{uuid4_filename(filename)}"
    
    try:
        # Read file contents
        content = await file.read()
        
        # 1. Upload to Supabase Storage first for cloud permanence
        object_storage.upload_file(user_id, filename, content)
        
        # 2. Save locally temporarily to allow parser to access it via path
        with open(temp_file_path, "wb") as f:
            f.write(content)
            
        # 3. Parse document
        parsed_pages = parser.parse(str(temp_file_path), filename)
        if not parsed_pages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document text could not be extracted or file is empty."
            )
            
        # 4. Chunk document text page-by-page
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = []
        for page in parsed_pages:
            split_texts = text_splitter.split_text(page["text"])
            for text_chunk in split_texts:
                chunks.append({
                    "text": text_chunk,
                    "page_number": page["page_number"],
                    "source": page["source"]
                })
                
        # 5. Generate embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = embedding_service.embed_texts(chunk_texts)
        
        # 6. Store in Qdrant
        vector_db.upsert_chunks(chunks, embeddings, user_id)
        
        return UploadResponse(
            filename=filename,
            chunks_count=len(chunks),
            message="Document successfully uploaded, parsed, and indexed."
        )
        
    except Exception as e:
        logger.error(f"Error handling upload of {filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document upload: {str(e)}"
        )
    finally:
        # Remove temporary file
        if temp_file_path.exists():
            os.remove(temp_file_path)

@router.post("/query", response_model=QueryResponse)
async def query_documents(
    payload: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    question = payload.question
    
    try:
        # 1. Embed query
        query_vector = embedding_service.embed_query(question)
        
        # 2. Search Qdrant for user's documents (top 5 results)
        relevant_chunks = vector_db.search(query_vector, user_id, top_k=5)
        
        # 3. Generate answer using Groq
        res = chat_service.generate_answer(question, relevant_chunks)
        
        return QueryResponse(
            answer=res["answer"],
            sources=res["sources"]
        )
    except Exception as e:
        logger.error(f"Error handling query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )

@router.get("/documents", response_model=List[str])
async def list_documents(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    try:
        # Get from Qdrant vector store
        docs = vector_db.get_user_documents(user_id)
        return docs
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document list: {str(e)}"
        )

@router.delete("/documents/{filename}", response_model=dict)
async def delete_document(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    try:
        # 1. Delete vectors from Qdrant
        vector_db.delete_document(user_id, filename)
        
        # 2. Delete file from Supabase Storage
        object_storage.delete_file(user_id, filename)
        
        return {"status": "success", "message": f"Document '{filename}' successfully deleted."}
    except Exception as e:
        logger.error(f"Error deleting document {filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )

def uuid4_filename(filename: str) -> str:
    ext = Path(filename).suffix
    return f"{uuid.uuid4()}{ext}"

# Make sure uuid import is available
import uuid
