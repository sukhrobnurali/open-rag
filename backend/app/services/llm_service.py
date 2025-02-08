import openai
from typing import List, Dict
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.max_tokens = 1000
        self.temperature = 0.1
    
    def generate_answer(self, question: str, context_chunks: List[Dict]) -> str:
        """Generate answer using retrieved context."""
        try:
            # Build context from chunks
            context = self._build_context(context_chunks)
            
            # Create prompt
            prompt = self._create_prompt(question, context)
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful AI assistant that answers questions based on provided document context. 
                        
                        Rules:
                        1. Only use information from the provided context
                        2. If the context doesn't contain enough information, say so
                        3. Be concise but comprehensive
                        4. Cite specific parts of the context when possible
                        5. If asked about something not in the context, politely decline"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer of {len(answer)} characters")
            
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise Exception(f"Answer generation failed: {e}")
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks."""
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Context {i}]")
            context_parts.append(chunk["content"])
            context_parts.append("")  # Empty line separator
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create the prompt for the LLM."""
        return f"""Based on the following context, please answer the question.

Context:
{context}

Question: {question}

Answer:"""
    
    def summarize_document(self, text: str, max_length: int = 200) -> str:
        """Generate a summary of document text."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant that creates concise summaries. Keep summaries under {max_length} words."
                    },
                    {
                        "role": "user",
                        "content": f"Please provide a concise summary of the following text:\n\n{text}"
                    }
                ],
                max_tokens=max_length * 2,  # Rough estimate for tokens
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return "Summary generation failed."