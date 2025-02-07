from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.models import Filter, FieldCondition, Range, MatchValue
from typing import List, Dict, Optional
import uuid
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class VectorService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        self.collection_name = "documents"
        self.vector_size = 1536  # OpenAI ada-002 embedding size
        
        # Initialize collection
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the collection exists."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Failed to ensure collection: {e}")
            raise Exception(f"Vector database initialization failed: {e}")
    
    def store_chunks(self, document_id: int, chunks: List[Dict]) -> List[str]:
        """Store document chunks in vector database."""
        if not chunks:
            return []
        
        points = []
        vector_ids = []
        
        for chunk in chunks:
            vector_id = str(uuid.uuid4())
            vector_ids.append(vector_id)
            
            point = PointStruct(
                id=vector_id,
                vector=chunk["embedding"],
                payload={
                    "document_id": document_id,
                    "chunk_index": chunk["index"],
                    "content": chunk["content"],
                    "word_count": chunk["word_count"]
                }
            )
            points.append(point)
        
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Stored {len(points)} chunks for document {document_id}")
            return vector_ids
            
        except Exception as e:
            logger.error(f"Failed to store chunks: {e}")
            raise Exception(f"Vector storage failed: {e}")
    
    def search_similar(
        self, 
        query_embedding: List[float], 
        limit: int = 5,
        document_id: Optional[int] = None,
        score_threshold: float = 0.7
    ) -> List[Dict]:
        """Search for similar chunks."""
        try:
            search_filter = None
            if document_id:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "document_id": result.payload["document_id"],
                    "chunk_index": result.payload["chunk_index"],
                    "content": result.payload["content"],
                    "word_count": result.payload["word_count"]
                })
            
            logger.info(f"Found {len(formatted_results)} similar chunks")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            raise Exception(f"Vector search failed: {e}")
    
    def delete_document_chunks(self, document_id: int):
        """Delete all chunks for a document."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            )
            logger.info(f"Deleted chunks for document {document_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete document chunks: {e}")
            raise Exception(f"Vector deletion failed: {e}")
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "total_points": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}