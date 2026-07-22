import os
from pathlib import Path
from dotenv import load_dotenv

# Find the root .env file (two levels up from backend/app/core/config.py -> c:\Users\omkar\Desktop\DocPilot AI)
base_dir = Path(__file__).resolve().parent.parent.parent.parent
dotenv_path = base_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "") or os.getenv("VITE_SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "") or os.getenv("VITE_SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "docpilot_docs")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    @property
    def CORS_ORIGINS(self) -> list:
        """Read CORS origins from environment variable (comma-separated) with localhost fallbacks."""
        env_origins = os.getenv("CORS_ORIGINS", "")
        origins = [o.strip() for o in env_origins.split(",") if o.strip()] if env_origins else []
        # Always include localhost for development
        default_origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ]
        return list(set(origins + default_origins))

settings = Settings()
