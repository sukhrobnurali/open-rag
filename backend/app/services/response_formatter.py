from typing import List, Dict
import re
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter:
    def __init__(self):
        self.max_source_content_length = 200
    
    def format_response(
        self,
        question: str,
        answer: str,
        chunks: List[Dict],
        processing_time_ms: int
    ) -> Dict:
        """Format the complete query response."""
        try:
            # Format sources
            sources = self._format_sources(chunks)
            
            # Clean and format answer
            formatted_answer = self._format_answer(answer)
            
            return {
                "question": question,
                "answer": formatted_answer,
                "sources": sources,
                "processing_time_ms": processing_time_ms
            }
            
        except Exception as e:
            logger.error(f"Failed to format response: {e}")
            return {
                "question": question,
                "answer": "Response formatting failed.",
                "sources": [],
                "processing_time_ms": processing_time_ms
            }
    
    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Format source information from chunks."""
        sources = []
        
        for chunk in chunks:
            # Truncate content if too long
            content = chunk["content"]
            if len(content) > self.max_source_content_length:
                content = content[:self.max_source_content_length] + "..."
            
            source = {
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "content": content,
                "score": round(chunk["score"], 3),
                "filename": chunk.get("document_filename", "Unknown"),
                "file_type": chunk.get("document_type", "Unknown")
            }
            
            sources.append(source)
        
        # Sort by relevance score (highest first)
        sources.sort(key=lambda x: x["score"], reverse=True)
        
        return sources
    
    def _format_answer(self, answer: str) -> str:
        """Clean and format the LLM answer."""
        if not answer:
            return "I couldn't generate an answer based on the available information."
        
        # Remove extra whitespace
        answer = re.sub(r'\s+', ' ', answer.strip())
        
        # Ensure proper sentence endings
        if answer and not answer.endswith(('.', '!', '?')):
            answer += '.'
        
        return answer
    
    def format_error_response(self, question: str, error_message: str) -> Dict:
        """Format error response."""
        return {
            "question": question,
            "answer": f"I encountered an error while processing your question: {error_message}",
            "sources": [],
            "processing_time_ms": 0
        }
    
    def format_chat_history(self, history: List[Dict]) -> List[Dict]:
        """Format chat history for display."""
        formatted_history = []
        
        for entry in history:
            formatted_entry = {
                "timestamp": entry.get("timestamp"),
                "question": entry.get("question"),
                "answer": self._format_answer(entry.get("answer", "")),
                "sources_count": len(entry.get("sources", []))
            }
            formatted_history.append(formatted_entry)
        
        return formatted_history