from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import os
import uuid
from typing import List

from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService
from app.services.query_service import QueryService
from app.config import settings

router = APIRouter()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)

# Initialize services
document_service = DocumentService()
query_service = QueryService()

ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.doc', '.docx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file type
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content to check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size {len(content)} exceeds maximum allowed size of {MAX_FILE_SIZE} bytes"
        )
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())
    filename = f"{unique_id}{file_extension}"
    file_path = os.path.join(settings.upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create database record
    db_document = Document(
        filename=filename,
        original_filename=file.filename,
        file_path=file_path,
        file_type=file_extension,
        file_size=len(content),
        status="uploaded"
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return DocumentUploadResponse(
        document_id=db_document.id,
        filename=db_document.original_filename,
        status=db_document.status,
        message="Document uploaded successfully"
    )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/{document_id}/process")
async def process_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status not in ["uploaded", "failed"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Document cannot be processed. Current status: {document.status}"
        )
    
    # Start processing
    success = await document_service.process_document(document_id, db)
    
    if success:
        return {"message": "Document processing completed successfully", "document_id": document_id}
    else:
        raise HTTPException(status_code=500, detail="Document processing failed")


@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    success = document_service.delete_document(document_id, db)
    if success:
        return {"message": "Document deleted successfully", "document_id": document_id}
    else:
        raise HTTPException(status_code=404, detail="Document not found or deletion failed")


@router.get("/{document_id}/chunks")
async def get_document_chunks(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    chunks = document_service.get_document_chunks(document_id, db)
    return {
        "document_id": document_id,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "index": chunk.chunk_index,
                "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                "vector_id": chunk.vector_id
            }
            for chunk in chunks
        ]
    }


@router.get("/{document_id}/summary")
async def get_document_summary(document_id: int, db: Session = Depends(get_db)):
    """Get AI-generated summary of a document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Document must be processed before generating summary. Current status: {document.status}"
        )
    
    try:
        summary = await query_service.get_document_summary(document_id, db)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")