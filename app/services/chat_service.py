# app/services/chat_service.py

import logging
from typing import Generator
from app.config.settings import settings
from app.services.vector_store_service import vector_store_service

logger = logging.getLogger("app")


class ChatService:
    def __init__(self):
        self._openai_client = None
        self.vector_store = vector_store_service
        self.model = settings.OPENAI_MODEL
        logger.info("ChatService initialized.")

    @property
    def openai_client(self):
        if self._openai_client is None:
            from openai import OpenAI
            if not settings.OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY is not set. Please add it to your .env file.")
            self._openai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENAI_API_KEY
            )
        return self._openai_client

    def _format_context(self, context_chunks: list[dict]) -> str:
        """Formats retrieved context for the prompt."""
        if not context_chunks:
            return "No relevant context found."

        context_str = ""
        for i, chunk in enumerate(context_chunks):
            # The payload of the hit is the original chunk dictionary
            context_str += f"--- Context Chunk {i+1} ---\n"
            context_str += chunk.get("text", "")
            context_str += "\n\n"
        return context_str.strip()

    def generate_response_stream(self, query: str) -> Generator[str, None, None]:
        """Generates a streamed response using retrieved context."""
        logger.info(f"Received query for chat: '{query}'")

        # 1. Retrieve context from the vector store
        context_chunks = self.vector_store.search(query, top_k=3)
        formatted_context = self._format_context(context_chunks)

        # 2. Generate response with a stream from OpenAI
        system_prompt = """You are a helpful AI assistant. Answer questions based ONLY on the provided context.
        If the context doesn't contain the answer, state "I don't have enough information to answer this question."
        Do not use any external knowledge."""

        user_prompt = f"Context:\n{formatted_context}\n\nQuestion: {query}"

        try:
            stream = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=True,
                temperature=0.5,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"Error during OpenAI stream: {e}")
            yield "Sorry, an error occurred while generating the response."


# Create a single instance to be used across the application
chat_service = ChatService()
