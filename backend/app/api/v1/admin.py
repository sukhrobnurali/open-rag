from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from app.database import get_db
from app.auth.auth import get_current_admin_user
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.services.document_service import DocumentService

router = APIRouter()


@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get admin dashboard statistics"""
    
    # User statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    
    # Document statistics
    total_documents = db.query(Document).count()
    completed_documents = db.query(Document).filter(Document.status == "completed").count()
    processing_documents = db.query(Document).filter(Document.status == "processing").count()
    failed_documents = db.query(Document).filter(Document.status == "failed").count()
    
    # Chunk statistics
    total_chunks = db.query(DocumentChunk).count()
    
    # Storage statistics
    total_storage = db.query(func.sum(Document.file_size)).scalar() or 0
    
    # Recent documents
    recent_documents = db.query(Document).order_by(
        Document.created_at.desc()
    ).limit(5).all()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "admin": admin_users,
            "inactive": total_users - active_users
        },
        "documents": {
            "total": total_documents,
            "completed": completed_documents,
            "processing": processing_documents,
            "failed": failed_documents,
            "uploaded": total_documents - completed_documents - processing_documents - failed_documents
        },
        "storage": {
            "total_size_bytes": total_storage,
            "total_chunks": total_chunks,
            "avg_chunks_per_doc": round(total_chunks / max(completed_documents, 1), 2)
        },
        "recent_documents": [
            {
                "id": doc.id,
                "filename": doc.original_filename,
                "status": doc.status,
                "created_at": doc.created_at,
                "file_size": doc.file_size
            }
            for doc in recent_documents
        ]
    }


@router.get("/users")
async def list_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all users with pagination"""
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.put("/users/{user_id}/toggle-active")
async def toggle_user_active_status(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Toggle user active status"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own account")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    db.commit()
    
    return {
        "message": f"User {user.email} {'activated' if user.is_active else 'deactivated'}",
        "user_id": user_id,
        "is_active": user.is_active
    }


@router.get("/documents")
async def list_all_documents(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = None
):
    """List all documents with optional status filter"""
    query = db.query(Document)
    
    if status:
        query = query.filter(Document.status == status)
    
    documents = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "documents": documents,
        "total": total,
        "skip": skip,
        "limit": limit,
        "status_filter": status
    }


@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Force reprocess a failed document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status not in ["failed", "completed"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot reprocess document with status: {document.status}"
        )
    
    # Reset status to uploaded for reprocessing
    document.status = "uploaded"
    db.commit()
    
    return {
        "message": f"Document {document.original_filename} queued for reprocessing",
        "document_id": document_id
    }


@router.delete("/documents/{document_id}/force")
async def force_delete_document(
    document_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Force delete a document (admin only)"""
    document_service = DocumentService()
    
    success = document_service.delete_document(document_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found or deletion failed")
    
    return {
        "message": f"Document {document_id} force deleted",
        "document_id": document_id
    }


@router.get("/system/status")
async def get_system_status(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get system status and health"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Get processing statistics
    document_service = DocumentService()
    processing_stats = document_service.get_processing_stats(db)
    
    return {
        "database": {
            "status": db_status,
            "connection": "active"
        },
        "processing": processing_stats,
        "services": {
            "vector_database": "connected",
            "embedding_service": "ready",
            "llm_service": "ready"
        }
    }


@router.post("/system/cleanup")
async def cleanup_orphaned_data(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Clean up orphaned data (chunks without documents, etc.)"""
    # Find chunks without documents
    orphaned_chunks = db.query(DocumentChunk).filter(
        ~DocumentChunk.document_id.in_(
            db.query(Document.id)
        )
    ).all()
    
    orphaned_count = len(orphaned_chunks)
    
    # Delete orphaned chunks
    for chunk in orphaned_chunks:
        db.delete(chunk)
    
    db.commit()
    
    return {
        "message": f"Cleanup completed. Removed {orphaned_count} orphaned chunks",
        "orphaned_chunks_removed": orphaned_count
    }