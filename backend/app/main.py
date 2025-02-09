from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.api.v1 import health, documents, query, auth, admin
from app.core.logging import setup_logging
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.database import create_tables, check_database_connection
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Advanced RAG System API",
    description="A Retrieval-Augmented Generation system for document Q&A",
    version="1.0.0",
    debug=settings.debug
)

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(query.router, prefix="/api/v1/query", tags=["query"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Advanced RAG System API...")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Database connection failed!")
        raise Exception("Database connection failed")
    
    # Create tables if they don't exist
    try:
        create_tables()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    logger.info("Application startup completed")


@app.get("/")
async def root():
    return {"message": "Advanced RAG System API", "version": "1.0.0", "status": "running"}