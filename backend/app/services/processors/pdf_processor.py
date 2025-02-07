import PyPDF2
from typing import List, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page_text
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue
                
                return text.strip()
        
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {file_path}: {e}")
            raise Exception(f"PDF processing failed: {e}")
    
    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        """Split text into overlapping chunks."""
        if not text:
            return []
        
        chunks = []
        words = text.split()
        
        if len(words) <= self.chunk_size:
            return [{
                "index": 0,
                "content": text,
                "word_count": len(words)
            }]
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "index": len(chunks),
                "content": chunk_text,
                "word_count": len(chunk_words)
            })
            
            # Break if we've reached the end
            if i + self.chunk_size >= len(words):
                break
        
        return chunks
    
    def process_pdf(self, file_path: str) -> List[Dict[str, any]]:
        """Process PDF file and return chunks."""
        logger.info(f"Processing PDF: {file_path}")
        
        # Extract text
        text = self.extract_text(file_path)
        if not text:
            raise Exception("No text extracted from PDF")
        
        logger.info(f"Extracted {len(text)} characters from PDF")
        
        # Create chunks
        chunks = self.chunk_text(text)
        logger.info(f"Created {len(chunks)} chunks from PDF")
        
        return chunks