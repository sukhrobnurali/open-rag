from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.database import get_db
from app.services.query_service import QueryService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize query service
query_service = QueryService()


class QueryRequest(BaseModel):
    question: str
    document_id: Optional[int] = None
    max_results: Optional[int] = 5
    score_threshold: Optional[float] = 0.7


class SourceInfo(BaseModel):
    document_id: int
    chunk_index: int
    content: str
    score: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceInfo]
    processing_time_ms: int


@router.post("/", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Query documents and get AI-generated answers with sources."""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"Processing query: {request.question[:100]}...")
        
        # Process query
        result = await query_service.process_query(
            question=request.question,
            document_id=request.document_id,
            max_results=request.max_results,
            score_threshold=request.score_threshold,
            db=db
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.get("/health")
async def query_health():
    """Health check for query service."""
    return {
        "status": "healthy",
        "service": "query-service",
        "components": {
            "embedding_service": "ready",
            "vector_database": "ready",
            "llm_service": "ready"
        }
    }