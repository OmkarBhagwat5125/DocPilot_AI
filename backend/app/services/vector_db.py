import logging
import uuid
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client import models
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION
        
        # Connect to Qdrant Cloud if URL is provided, otherwise fall back to local disk persistence
        if settings.QDRANT_URL:
            logger.info(f"Connecting to Qdrant Cloud at {settings.QDRANT_URL}...")
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY
            )
        else:
            # Set up local database folder in project root
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            db_path = base_dir / "qdrant_db"
            logger.info(f"Connecting to local Qdrant database at {db_path}...")
            self.client = QdrantClient(path=str(db_path))
            
        self.ensure_collection()

    def ensure_collection(self):
        try:
            # Check if collection exists
            exists = self.client.collection_exists(self.collection_name)
            if not exists:
                logger.info(f"Creating Qdrant collection: {self.collection_name} (384 dimensions, Cosine distance)...")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=384,  # bge-small-en-v1.5 dimension size
                        distance=models.Distance.COSINE
                    )
                )
                logger.info("Qdrant collection created successfully.")
            else:
                logger.info(f"Qdrant collection '{self.collection_name}' already exists.")
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection exists: {str(e)}")
            raise e

    def upsert_chunks(self, chunks: list[dict], embeddings: list[list[float]], user_id: str):
        if not chunks or not embeddings:
            logger.warning("Empty chunks or embeddings. Skipping upsert.")
            return

        points = []
        for idx, chunk in enumerate(chunks):
            point_id = str(uuid.uuid4())
            payload = {
                "text": chunk.get("text", ""),
                "page_number": chunk.get("page_number", 1),
                "source": chunk.get("source", ""),
                "user_id": user_id
            }
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=embeddings[idx],
                    payload=payload
                )
            )

        try:
            logger.info(f"Upserting {len(points)} vectors to Qdrant for user: {user_id}")
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info("Upsert completed successfully.")
        except Exception as e:
            logger.error(f"Failed to upsert points to Qdrant: {str(e)}")
            raise e

    def search(self, query_embedding: list[float], user_id: str, top_k: int = 5) -> list[dict]:
        try:
            logger.info(f"Searching Qdrant for user {user_id} (top_k={top_k})...")
            
            # Apply filter to ensure user privacy and isolation
            search_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            )
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=top_k
            )
            
            mapped_results = []
            for hit in results:
                payload = hit.payload or {}
                mapped_results.append({
                    "text": payload.get("text", ""),
                    "page_number": payload.get("page_number", 1),
                    "source": payload.get("source", ""),
                    "score": hit.score
                })
                
            return mapped_results
        except Exception as e:
            logger.error(f"Failed to search Qdrant: {str(e)}")
            return []

    def delete_document(self, user_id: str, source: str):
        try:
            logger.info(f"Deleting document '{source}' vectors for user: {user_id}")
            
            # Filter matches both user_id and document source (filename)
            delete_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    ),
                    models.FieldCondition(
                        key="source",
                        match=models.MatchValue(value=source)
                    )
                ]
            )
            
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(filter=delete_filter)
            )
            logger.info(f"Successfully deleted document '{source}' from Qdrant.")
        except Exception as e:
            logger.error(f"Failed to delete document '{source}' from Qdrant: {str(e)}")
            raise e

    def get_user_documents(self, user_id: str) -> list[str]:
        try:
            logger.info(f"Fetching unique documents indexed for user: {user_id}")
            
            # Filter by user_id
            user_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            )
            
            # Scroll points in the collection (max 1000 for list metadata)
            offset = None
            unique_sources = set()
            
            while True:
                res, next_offset = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=user_filter,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                for point in res:
                    payload = point.payload or {}
                    source = payload.get("source")
                    if source:
                        unique_sources.add(source)
                        
                if not next_offset:
                    break
                offset = next_offset
                
            return list(unique_sources)
        except Exception as e:
            logger.error(f"Failed to get user documents from Qdrant: {str(e)}")
            return []

vector_db = VectorDBService()
