from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import health, documents, query

app = FastAPI(
    title="Advanced RAG System API",
    description="A Retrieval-Augmented Generation system for document Q&A",
    version="1.0.0",
    debug=settings.debug
)

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
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(query.router, prefix="/api/v1/query", tags=["query"])


@app.get("/")
async def root():
    return {"message": "Advanced RAG System API", "version": "1.0.0"}