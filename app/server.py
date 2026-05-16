# app/server.py

import logging
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from logging_config.config import LOGGING_CONFIG
from app.api.router import api_router
from app.services.vector_store_service import vector_store_service

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🧠 DocMind AI starting up...")
    from app.config.settings import settings
    if settings.QDRANT_URL:
        logger.info("Initializing Qdrant collection...")
        try:
            vector_store_service.initialize_collection()
            logger.info("Qdrant collection initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}")
    else:
        logger.warning("QDRANT_URL not set -- vector store disabled. Add credentials to .env file.")
    yield
    logger.info("DocMind AI shutting down...")


app = FastAPI(
    title="DocMind AI — Intelligent Document Chat",
    description="Upload PDFs, ask questions, get AI-powered answers from your documents.",
    version="0.1.0",
    lifespan=lifespan,
)

# TODO: Fix origins in final version
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
