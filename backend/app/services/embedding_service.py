import openai
from typing import List, Dict
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = settings.openai_api_key


class EmbeddingService:
    def __init__(self, model: str = "text-embedding-ada-002"):
        self.model = model
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            raise Exception(f"Embedding generation failed: {e}")
    
    def get_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Get embeddings for multiple texts in batches."""
        if not texts:
            return []
        
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                
                logger.info(f"Generated embeddings for batch {i//batch_size + 1}, texts {i+1}-{min(i+batch_size, len(texts))}")
            
            except Exception as e:
                logger.error(f"Failed to get embeddings for batch {i//batch_size + 1}: {e}")
                raise Exception(f"Batch embedding generation failed: {e}")
        
        return embeddings
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Add embeddings to document chunks."""
        if not chunks:
            return []
        
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.get_embeddings_batch(texts)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding
        
        logger.info(f"Added embeddings to {len(chunks)} chunks")
        return chunks