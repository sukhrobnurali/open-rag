# Advanced RAG System

A Retrieval-Augmented Generation (RAG) system that allows users to upload documents and ask questions about them using AI.

## Features

- Upload multiple document types (PDFs, images, text files)
- Ask questions in natural language
- Get AI-powered answers with source citations
- Web interface for easy use
- RESTful API for developers

## Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: React, TypeScript
- **Database**: PostgreSQL (metadata), Qdrant (vectors)
- **LLM**: OpenAI GPT-4
- **Deployment**: Docker

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your API keys
3. Run with Docker:
   ```bash
   docker-compose up -d
   ```
4. Access the web interface at `http://localhost:3000`

## Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Architecture

```
User → Web UI → FastAPI Backend → Document Processor
                     ↓
               Vector Database ← Embeddings
                     ↓
                Query Engine → LLM → Response
```

## License

MIT License