# app/services/document_service.py

import logging
import io
import os
import tempfile
import asyncio
from typing import List, Dict
from pathlib import Path

from google import genai
from llama_parse import LlamaParse
from llama_index.core import Document
from llama_index.core.node_parser import HierarchicalNodeParser
from llama_index.core.node_parser import get_leaf_nodes

from app.config.settings import settings

logger = logging.getLogger("app")


class DocumentService:
    def __init__(self):
        try:
            self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)

            self.llama_parser = LlamaParse(
                api_key=settings.LLAMA_CLOUD_API_KEY,
                result_type="markdown",
                verbose=True,
            )

            self.node_parser = HierarchicalNodeParser.from_defaults(
                chunk_sizes=[2048, 512]
            )

            self.gemini_supported_ext = {".pdf"}
            self.llamaparse_supported_ext = {".docx", ".doc", ".pptx", ".ppt"}
            self.direct_supported_ext = {".txt", ".md"}

            logger.info(
                "DocumentService initialized with Gemini and LlamaParse clients."
            )
        except Exception as e:
            logger.error(f"Failed to initialize DocumentService: {e}")
            raise

    # --- Main Public Method ---
    def process_file(self, file_content: bytes, filename: str) -> str:
        """
        Processes an uploaded file based on its extension and returns its markdown content.
        """
        file_ext = Path(filename).suffix.lower()
        logger.info(
            f"Routing file '{filename}' with extension '{file_ext}' to appropriate parser."
        )

        if file_ext in self.gemini_supported_ext:
            return self._parse_pdf_with_gemini(file_content, filename)

        elif file_ext in self.llamaparse_supported_ext:
            # LlamaParse has an async API; we run it in a new event loop.
            # This is safe to do inside a background task.
            return asyncio.run(self._parse_with_llamaparse(file_content, filename))

        elif file_ext in self.direct_supported_ext:
            return self._parse_text_direct(file_content)

        else:
            logger.error(f"Unsupported file type for '{filename}': {file_ext}")
            raise ValueError(f"Unsupported file type: {file_ext}")

    # --- Private Helper Methods for Parsing ---
    def _parse_pdf_with_gemini(self, pdf_content: bytes, filename: str) -> str:
        """Parses a PDF file using the Gemini API."""
        logger.info(f"Parsing PDF '{filename}' with Gemini...")
        uploaded_file = None
        temp_file_path = None

        try:
            # Create a temporary file since client.files.upload expects a file path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name

            uploaded_file = self.gemini_client.files.upload(file=temp_file_path)
            logger.info(f"Successfully uploaded '{filename}' to Gemini File API.")

            # Prompt Gemini to process the uploaded file
            prompt = """Convert the contents of this PDF into well-formatted Markdown.
            Preserve all structural elements like headings, lists, tables, and paragraphs.
            Maintain the original formatting and hierarchy. Ensure the output is clean."""

            contents = [uploaded_file, prompt]
            response = self.gemini_client.models.generate_content(
                model=settings.GEMINI_MODEL, contents=contents
            )
            logger.info(f"Successfully parsed '{filename}' to markdown via Gemini.")
            return response.text

        except Exception as e:
            logger.error(f"Failed to parse PDF '{filename}' with Gemini: {e}")
            raise

        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

            # Clean up by deleting the file from Gemini's server
            if uploaded_file:
                logger.info(f"Deleting uploaded file '{filename}' from Gemini server.")
                self.gemini_client.files.delete(name=uploaded_file.name)

    async def _parse_with_llamaparse(self, file_content: bytes, filename: str) -> str:
        """Parses a document using the LlamaParse API."""
        logger.info(f"Parsing document '{filename}' with LlamaParse...")
        temp_file_path = None

        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(filename).suffix
            ) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            # Asynchronously parse the document. The SDK handles the upload.
            documents = await self.llama_parser.aload_data(temp_file_path)

            if not documents:
                raise ValueError("LlamaParse failed to return any content.")

            logger.info(f"Successfully parsed '{filename}' with LlamaParse.")
            return "\n\n".join(doc.get_content() for doc in documents)

        except Exception as e:
            logger.error(f"Failed to parse '{filename}' with LlamaParse: {e}")
            raise

        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")

    def _parse_text_direct(self, file_content: bytes) -> str:
        """'Parses' a plain text file by decoding it."""
        logger.info("Parsing plain text file directly.")

        try:
            return file_content.decode("utf-8")

        except UnicodeDecodeError:
            logger.warning("UTF-8 decoding failed, trying with latin-1 fallback.")
            return file_content.decode("latin-1")

    # --- Chunking Method ---
    def create_chunks(self, markdown_text: str, filename: str) -> List[Dict]:
        """Creates hierarchical chunks from markdown text."""
        logger.info(f"Creating chunks for '{filename}'...")
        doc = Document(text=markdown_text, metadata={"filename": filename})
        nodes = self.node_parser.get_nodes_from_documents([doc])
        leaf_nodes = get_leaf_nodes(nodes)

        chunks = []
        for node in leaf_nodes:
            chunk_data = {
                "id": node.node_id,
                "text": node.get_content(),
                "metadata": node.metadata,
            }
            chunks.append(chunk_data)

        logger.info(f"Created {len(chunks)} chunks for '{filename}'.")
        return chunks


# Note: The global instance is removed. Instances will be created where needed.
