# app/schemas/document.py

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    index_id: str = Field(..., description="The unique ID for the indexing job.")
    filename: str = Field(..., description="The name of the uploaded file.")


class IndexingStatusResponse(BaseModel):
    index_id: str = Field(..., description="The ID of the indexing job.")
    status: str = Field(
        ...,
        description="The current status of the job (e.g., processing, completed, failed).",
    )
    details: str | None = Field(
        None, description="Additional details about the status."
    )
