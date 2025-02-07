from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import os

from app.models.document import Document, DocumentChunk
from app.services.processors.pdf_processor import PDFProcessor
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
    
    async def process_document(self, document_id: int, db: Session) -> bool:
        """Process a document through the complete pipeline."""
        try:
            # Get document from database
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise Exception(f"Document {document_id} not found")
            
            logger.info(f"Starting processing for document {document_id}: {document.original_filename}")
            
            # Update status
            document.status = "processing"
            db.commit()
            
            # Step 1: Extract and chunk text
            chunks = self._extract_and_chunk(document)
            
            # Step 2: Generate embeddings
            chunks_with_embeddings = self.embedding_service.embed_chunks(chunks)
            
            # Step 3: Store in vector database
            vector_ids = self.vector_service.store_chunks(document_id, chunks_with_embeddings)
            
            # Step 4: Save chunks to database
            self._save_chunks_to_db(document_id, chunks_with_embeddings, vector_ids, db)
            
            # Update document status
            document.status = "completed"
            db.commit()
            
            logger.info(f"Successfully processed document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            
            # Update status to failed
            if document:
                document.status = "failed"
                db.commit()
            
            return False
    
    def _extract_and_chunk(self, document: Document) -> List[dict]:
        """Extract text and create chunks based on file type."""
        if document.file_type == ".pdf":
            return self.pdf_processor.process_pdf(document.file_path)
        
        elif document.file_type == ".txt":
            return self._process_text_file(document.file_path)
        
        else:
            raise Exception(f"Unsupported file type: {document.file_type}")
    
    def _process_text_file(self, file_path: str) -> List[dict]:
        """Process plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            return self.pdf_processor.chunk_text(text)
            
        except Exception as e:
            logger.error(f"Failed to process text file {file_path}: {e}")
            raise Exception(f"Text file processing failed: {e}")
    
    def _save_chunks_to_db(
        self, 
        document_id: int, 
        chunks: List[dict], 
        vector_ids: List[str], 
        db: Session
    ):
        """Save chunks to database."""
        try:
            for chunk, vector_id in zip(chunks, vector_ids):
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk["index"],
                    content=chunk["content"],
                    vector_id=vector_id
                )
                db.add(db_chunk)
            
            db.commit()
            logger.info(f"Saved {len(chunks)} chunks to database for document {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to save chunks to database: {e}")
            raise Exception(f"Database chunk storage failed: {e}")
    
    def delete_document(self, document_id: int, db: Session) -> bool:
        """Delete document and all associated data."""
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return False
            
            # Delete from vector database
            self.vector_service.delete_document_chunks(document_id)
            
            # Delete file from disk
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Delete from database (cascades to chunks)
            db.delete(document)
            db.commit()
            
            logger.info(f"Successfully deleted document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def get_document_chunks(self, document_id: int, db: Session) -> List[DocumentChunk]:
        """Get all chunks for a document."""
        return db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).all()
    
    def get_processing_stats(self, db: Session) -> dict:
        """Get processing statistics."""
        total_docs = db.query(Document).count()
        completed_docs = db.query(Document).filter(Document.status == "completed").count()
        processing_docs = db.query(Document).filter(Document.status == "processing").count()
        failed_docs = db.query(Document).filter(Document.status == "failed").count()
        
        vector_stats = self.vector_service.get_collection_stats()
        
        return {
            "total_documents": total_docs,
            "completed_documents": completed_docs,
            "processing_documents": processing_docs,
            "failed_documents": failed_docs,
            "vector_database": vector_stats
        }