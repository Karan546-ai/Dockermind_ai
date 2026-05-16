# app/schemas/chat.py

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user's query.")
