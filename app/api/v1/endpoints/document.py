# app/api/v1/endpoints/document.py

import uuid
import logging
from typing import List
from pathlib import Path
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    BackgroundTasks,
    HTTPException,
    status,
    Path as FastApiPath,
)
from app.schemas.document import UploadResponse, IndexingStatusResponse
from app.services.document_service import DocumentService
from app.services.vector_store_service import vector_store_service

logger = logging.getLogger("app")


class DocumentEndpoints:
    job_statuses = {}

    def __init__(self):
        self.router = APIRouter(tags=["Document"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/uploadfiles",
            self.upload_documents,
            methods=["POST"],
            response_model=List[UploadResponse],
            status_code=status.HTTP_202_ACCEPTED,
        )
        self.router.add_api_route(
            "/indexing_status/{index_id}",
            self.get_indexing_status,
            methods=["GET"],
            response_model=IndexingStatusResponse,
        )

    @staticmethod
    def run_indexing_pipeline(file_content: bytes, filename: str, job_id: str):
        """The background task for processing and indexing a document."""
        try:
            document_service_instance = DocumentService()
            logger.info(f"[{job_id}] Starting indexing pipeline for {filename}")
            DocumentEndpoints.job_statuses[job_id] = {
                "status": "processing",
                "details": "Parsing document...",
            }

            markdown = document_service_instance.process_file(file_content, filename)

            DocumentEndpoints.job_statuses[job_id][
                "details"
            ] = "Creating document chunks..."
            chunks = document_service_instance.create_chunks(markdown, filename)

            DocumentEndpoints.job_statuses[job_id][
                "details"
            ] = "Upserting chunks to vector store..."
            vector_store_service.upsert_chunks(chunks)

            DocumentEndpoints.job_statuses[job_id] = {
                "status": "completed",
                "details": f"Successfully indexed {filename}",
            }
            logger.info(f"[{job_id}] Indexing completed for {filename}")
        except Exception as e:
            logger.error(f"[{job_id}] Error during indexing: {e}")
            DocumentEndpoints.job_statuses[job_id] = {
                "status": "failed",
                "details": str(e),
            }

    async def upload_documents(
        self, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)
    ):
        """Uploads one or more files for asynchronous processing."""
        responses = []
        supported_extensions = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt", ".md"}

        for file in files:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in supported_extensions:
                logger.warning(f"Skipping unsupported file: {file.filename}")
                continue

            job_id = str(uuid.uuid4())
            file_content = await file.read()

            background_tasks.add_task(
                self.run_indexing_pipeline, file_content, file.filename, job_id
            )
            self.job_statuses[job_id] = {
                "status": "processing",
                "details": "Task received.",
            }
            responses.append(UploadResponse(index_id=job_id, filename=file.filename))

        if not responses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid or supported files were uploaded.",
            )
        return responses

    def get_indexing_status(
        self,
        index_id: str = FastApiPath(
            ..., description="The ID of the indexing job to check."
        ),
    ):
        """Retrieves the status of a document indexing job."""
        status_info = self.job_statuses.get(index_id)
        if not status_info:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Job ID not found.")
        return IndexingStatusResponse(
            index_id=index_id,
            status=status_info.get("status", "unknown"),
            details=status_info.get("details", ""),
        )
