import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DOCS_RAW_DIR = os.getenv("DOCS_RAW_DIR", "./data/raw")
    DOCS_PROCESSED_DIR = os.getenv("DOCS_PROCESSED_DIR", "./data/processed")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    # GROQ API
    GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", 8001))
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))
    TOP_K = int(os.getenv("TOP_K", 5))
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin_secret")

settings = Settings()
