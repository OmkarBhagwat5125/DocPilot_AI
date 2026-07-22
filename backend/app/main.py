import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from backend.app.core.config import settings
from backend.app.api.endpoints import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DocPilot AI API",
    description="Backend API for DocPilot AI document intelligence system",
    version="2.0.0"
)

# Set CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routes
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up DocPilot AI FastAPI Backend...")
    logger.info(f"CORS Origins configured: {settings.CORS_ORIGINS}")
    
    # Create upload directories
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    logger.info(f"Upload directory ensured at: {upload_dir.resolve()}")

@app.get("/")
async def root_endpoint():
    return {
        "status": "ok",
        "service": "DocPilot AI API",
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DocPilot AI API"}
