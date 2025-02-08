from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import time
import logging

from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
from app.services.response_formatter import ResponseFormatter
from app.models.document import Document

logger = logging.getLogger(__name__)


class QueryService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.llm_service = LLMService()
        self.response_formatter = ResponseFormatter()
    
    async def process_query(
        self,
        question: str,
        document_id: Optional[int] = None,
        max_results: int = 5,
        score_threshold: float = 0.7,
        db: Session = None
    ) -> Dict:
        """Process a query through the complete pipeline."""
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: '{question}' for document_id: {document_id}")
            
            # Step 1: Generate query embedding
            query_embedding = self.embedding_service.get_embedding(question)
            
            # Step 2: Retrieve similar chunks
            similar_chunks = self.vector_service.search_similar(
                query_embedding=query_embedding,
                limit=max_results,
                document_id=document_id,
                score_threshold=score_threshold
            )
            
            if not similar_chunks:
                return self._create_no_results_response(question, start_time)
            
            # Step 3: Enrich chunks with document metadata
            enriched_chunks = self._enrich_chunks_with_metadata(similar_chunks, db)
            
            # Step 4: Generate answer
            answer = self.llm_service.generate_answer(question, enriched_chunks)
            
            # Step 5: Format response
            response = self.response_formatter.format_response(
                question=question,
                answer=answer,
                chunks=enriched_chunks,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
            
            logger.info(f"Query processed successfully in {response['processing_time_ms']}ms")
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise Exception(f"Query processing failed: {e}")
    
    def _enrich_chunks_with_metadata(self, chunks: List[Dict], db: Session) -> List[Dict]:
        """Add document metadata to chunks."""
        if not db:
            return chunks
        
        enriched_chunks = []
        document_cache = {}
        
        for chunk in chunks:
            doc_id = chunk["document_id"]
            
            # Get document info (with caching)
            if doc_id not in document_cache:
                document = db.query(Document).filter(Document.id == doc_id).first()
                document_cache[doc_id] = document
            
            document = document_cache[doc_id]
            
            enriched_chunk = {
                **chunk,
                "document_filename": document.original_filename if document else "Unknown",
                "document_type": document.file_type if document else "Unknown"
            }
            
            enriched_chunks.append(enriched_chunk)
        
        return enriched_chunks
    
    def _create_no_results_response(self, question: str, start_time: float) -> Dict:
        """Create response when no relevant documents are found."""
        return {
            "question": question,
            "answer": "I couldn't find any relevant information in the uploaded documents to answer your question. Please try rephrasing your question or upload more relevant documents.",
            "sources": [],
            "processing_time_ms": int((time.time() - start_time) * 1000)
        }
    
    async def get_document_summary(self, document_id: int, db: Session) -> Dict:
        """Get AI-generated summary of a document."""
        try:
            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise Exception("Document not found")
            
            # Get some chunks for summary
            chunks = self.vector_service.search_similar(
                query_embedding=self.embedding_service.get_embedding("summary overview"),
                document_id=document_id,
                limit=3,
                score_threshold=0.0  # Get any chunks
            )
            
            if not chunks:
                return {"summary": "No content available for summary"}
            
            # Combine chunk content
            combined_text = "\n\n".join([chunk["content"] for chunk in chunks])
            
            # Generate summary
            summary = self.llm_service.summarize_document(combined_text)
            
            return {
                "document_id": document_id,
                "filename": document.original_filename,
                "summary": summary,
                "chunks_used": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate document summary: {e}")
            raise Exception(f"Summary generation failed: {e}")