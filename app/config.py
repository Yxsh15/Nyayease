from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./nyayease.db"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # API Keys
    GEMINI_API_KEY: str
    FIREBASE_CONFIG: Optional[str] = None
    GOOGLE_CLOUD_CREDENTIALS: Optional[str] = None
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt", ".doc", ".docx"}
    UPLOAD_DIR: str = "uploads"  # Added this
    
    # Logging
    LOG_LEVEL: str = "INFO"  # Added this
    
    class Config:
        env_file = ".env"

settings = Settings()