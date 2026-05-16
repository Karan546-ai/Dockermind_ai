# app/api/router.py

from fastapi import APIRouter

# Import endpoint classes
from app.api.v1.endpoints.health import HealthEndpoints
from app.api.v1.endpoints.chat import ChatEndpoints
from app.api.v1.endpoints.document import DocumentEndpoints

# Import service instances needed for dependency injection
from app.services.chat_service import chat_service

api_router = APIRouter()

# --- Instantiate Endpoint Classes and Inject Dependencies ---

# Health has no dependencies
health_endpoints = HealthEndpoints()

# Chat needs the chat_service
chat_endpoints = ChatEndpoints(chat_service=chat_service)

# Document has no external dependencies
document_endpoints = DocumentEndpoints()


# --- Include the routers from the endpoint instances ---

api_router.include_router(health_endpoints.router, prefix="/v1")
api_router.include_router(chat_endpoints.router, prefix="/v1")
api_router.include_router(document_endpoints.router, prefix="/v1")
