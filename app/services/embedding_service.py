# app/services/embedding_service.py

import logging
from typing import List
from app.config.settings import settings
from google import genai

logger = logging.getLogger("app")


class EmbeddingService:
    def __init__(self):
        self._client = None
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL if settings.OPENAI_EMBEDDING_MODEL else "text-embedding-004"
        self.embedding_dimension = settings.OPENAI_EMBEDDING_DIMENSION
        logger.info(
            f"EmbeddingService initialized with Gemini model: {self.embedding_model}"
        )

    @property
    def client(self):
        if self._client is None:
            if not settings.GEMINI_API_KEY:
                raise RuntimeError("GEMINI_API_KEY is not set. Please add it to your .env file.")
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    def get_embedding_dimension(self) -> int:
        """Returns the dimension of the embeddings."""
        return self.embedding_dimension

    def create_embedding(self, text: str) -> List[float]:
        """Creates an embedding for a given text using Gemini."""
        if not text.strip():
            logger.warning("Attempted to embed empty or whitespace-only string.")
            return [0.0] * self.embedding_dimension

        try:
            # Replace newlines
            text = text.replace("\n", " ")
            response = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text,
            )
            # The structure of the response depends on the google-genai version, typically response.embeddings[0].values
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Failed to create Gemini embedding: {e}")
            raise


# A single instance to be used throughout the app
embedding_service = EmbeddingService()

