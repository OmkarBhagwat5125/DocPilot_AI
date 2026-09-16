"""Bounded upload buffering and batched vector indexing."""
from pathlib import Path

from fastapi import HTTPException, UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter


async def save_upload(file: UploadFile, destination: Path, max_bytes: int) -> None:
    if file.size is not None and file.size > max_bytes:
        raise HTTPException(413, "File exceeds the configured upload size limit.")
    total = 0
    with destination.open("wb") as output:
        while data := await file.read(1024 * 1024):
            total += len(data)
            if total > max_bytes:
                raise HTTPException(413, "File exceeds the configured upload size limit.")
            output.write(data)


def index_pages(pages, user_id, embedder, database, batch_size: int) -> int:
    """Do not retain vectors for the entire document before writing them."""
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    batch = []
    count = 0

    def write_batch():
        vectors = embedder.embed_texts([chunk["text"] for chunk in batch])
        database.upsert_chunks(batch, vectors, user_id)

    for page in pages:
        for text in splitter.split_text(page["text"]):
            batch.append({"text": text, "page_number": page["page_number"], "source": page["source"]})
            if len(batch) == batch_size:
                write_batch()
                count += len(batch)
                batch = []
    if batch:
        write_batch()
        count += len(batch)
    return count
