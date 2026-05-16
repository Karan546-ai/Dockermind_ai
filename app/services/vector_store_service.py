# app/services/vector_store_service.py

import logging
from typing import List, Dict
from app.config.settings import settings
from app.services.embedding_service import EmbeddingService, embedding_service

logger = logging.getLogger("app")


class VectorStoreService:
    def __init__(self, embedding_service: EmbeddingService):
        self._client = None
        self.embedding_service = embedding_service
        self.collection_name = settings.QDRANT_COLLECTION

    @property
    def client(self):
        if self._client is None:
            from qdrant_client import QdrantClient
            if not settings.QDRANT_URL or settings.QDRANT_URL == ":memory:":
                self._client = QdrantClient(location=":memory:")
            else:
                self._client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        return self._client

    def initialize_collection(self):
        """Creates the Qdrant collection if it doesn't exist."""
        from qdrant_client import models
        try:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_service.get_embedding_dimension(),
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info(
                f"Collection '{self.collection_name}' created or already exists."
            )
        except Exception as e:
            logger.error(f"Failed to create Qdrant collection: {e}")
            # If it's a 409 conflict, it means it exists, which is fine.
            # For other errors, we should raise them.
            if "already exists" not in str(e).lower():
                raise

    def upsert_chunks(self, chunks: List[Dict]):
        """Embeds and upserts document chunks into Qdrant."""
        from qdrant_client import models
        points = []
        for i, chunk in enumerate(chunks):
            vector = self.embedding_service.create_embedding(chunk["text"])
            point = models.PointStruct(
                id=chunk["id"],  # Using the node_id from LlamaIndex as the point ID
                vector=vector,
                payload=chunk,  # Store the entire chunk dict as payload
            )
            points.append(point)

        if not points:
            logger.warning("No chunks to upsert.")
            return

        logger.info(f"Upserting {len(points)} points to '{self.collection_name}'...")
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        logger.info("Upsert complete.")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Performs a similarity search in Qdrant."""
        query_vector = self.embedding_service.create_embedding(query)
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
        )
        # The payload of each hit is the original chunk dictionary
        return [hit.payload for hit in search_result]


# Create a single service instance for the app (lazy — no connection until first use)
vector_store_service = VectorStoreService(embedding_service=embedding_service)
