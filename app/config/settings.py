# app/config/settings.py

import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("app")


class Settings(BaseSettings):
    # To load from a .env file
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # API Keys (optional so the server can start without them)
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLAMA_CLOUD_API_KEY: str = ""

    # Model Settings
    GEMINI_MODEL: str = "gemini-2.5-pro"
    OPENAI_MODEL: str = "gpt-4.1"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSION: int = 1536  # Dimension for text-embedding-3-small

    # Qdrant Settings
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "documents"


# Create a single instance to be used across the application
settings = Settings()
