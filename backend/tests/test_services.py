import pytest
from unittest.mock import Mock, patch
from app.services.processors.pdf_processor import PDFProcessor
from app.services.response_formatter import ResponseFormatter


class TestPDFProcessor:
    def test_chunk_text_small(self):
        processor = PDFProcessor(chunk_size=10, chunk_overlap=2)
        text = "This is a short text."
        chunks = processor.chunk_text(text)
        
        assert len(chunks) == 1
        assert chunks[0]["content"] == text
        assert chunks[0]["index"] == 0

    def test_chunk_text_large(self):
        processor = PDFProcessor(chunk_size=5, chunk_overlap=1)
        words = ["word"] * 15
        text = " ".join(words)
        chunks = processor.chunk_text(text)
        
        assert len(chunks) > 1
        assert all(chunk["word_count"] <= 5 for chunk in chunks)

    def test_empty_text(self):
        processor = PDFProcessor()
        chunks = processor.chunk_text("")
        assert chunks == []


class TestResponseFormatter:
    def test_format_sources(self):
        formatter = ResponseFormatter()
        chunks = [
            {
                "document_id": 1,
                "chunk_index": 0,
                "content": "This is a test content that is longer than the max length limit to test truncation",
                "score": 0.85,
                "document_filename": "test.pdf",
                "document_type": ".pdf"
            }
        ]
        
        sources = formatter._format_sources(chunks)
        
        assert len(sources) == 1
        assert sources[0]["score"] == 0.85
        assert len(sources[0]["content"]) <= formatter.max_source_content_length + 3  # +3 for "..."

    def test_format_answer(self):
        formatter = ResponseFormatter()
        
        # Test normal answer
        answer = formatter._format_answer("This is an answer")
        assert answer == "This is an answer."
        
        # Test answer with existing punctuation
        answer = formatter._format_answer("This is an answer!")
        assert answer == "This is an answer!"
        
        # Test empty answer
        answer = formatter._format_answer("")
        assert "couldn't generate" in answer.lower()

    def test_format_response(self):
        formatter = ResponseFormatter()
        chunks = [{
            "document_id": 1,
            "chunk_index": 0,
            "content": "Test content",
            "score": 0.9,
            "document_filename": "test.pdf",
            "document_type": ".pdf"
        }]
        
        response = formatter.format_response(
            question="Test question?",
            answer="Test answer",
            chunks=chunks,
            processing_time_ms=100
        )
        
        assert response["question"] == "Test question?"
        assert response["answer"] == "Test answer."
        assert len(response["sources"]) == 1
        assert response["processing_time_ms"] == 100