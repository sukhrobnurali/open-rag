from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "rag-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/health/db")
async def database_health():
    # TODO: Add actual database connectivity check
    return {
        "status": "healthy",
        "service": "database",
        "timestamp": datetime.utcnow().isoformat()
    }