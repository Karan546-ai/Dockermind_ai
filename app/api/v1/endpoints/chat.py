# app/api/v1/endpoints/chat.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService


class ChatEndpoints:
    def __init__(self, chat_service: ChatService):
        self.router = APIRouter(tags=["Chat"])
        self.chat_service = chat_service
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/chat",
            self.stream_chat_response,
            methods=["POST"],
        )

    def stream_chat_response(self, request: ChatRequest):
        """Handles a user query and streams the RAG response back."""
        return StreamingResponse(
            self.chat_service.generate_response_stream(request.query),
            media_type="text/plain",
        )
