#!/bin/bash

# Advanced RAG System Setup Script

set -e

echo "🚀 Setting up Advanced RAG System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before continuing!"
    echo "   Required: OPENAI_API_KEY, SECRET_KEY, JWT_SECRET_KEY"
    read -p "Press Enter when you've configured your .env file..."
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/uploads
mkdir -p data/logs

# Pull and start services
echo "🐳 Starting Docker services..."
docker-compose pull
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are healthy
echo "🔍 Checking service health..."

# Check PostgreSQL
until docker-compose exec postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Check Qdrant
until curl -s http://localhost:6333/health > /dev/null 2>&1; do
    echo "Waiting for Qdrant..."
    sleep 2
done
echo "✅ Qdrant is ready"

# Check Backend API
until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    echo "Waiting for Backend API..."
    sleep 2
done
echo "✅ Backend API is ready"

# Check Frontend
until curl -s http://localhost:3000 > /dev/null 2>&1; do
    echo "Waiting for Frontend..."
    sleep 2
done
echo "✅ Frontend is ready"

echo ""
echo "🎉 Setup complete! Your RAG system is now running:"
echo ""
echo "   🌐 Frontend:  http://localhost:3000"
echo "   🔧 Backend:   http://localhost:8000"
echo "   📚 API Docs:  http://localhost:8000/docs"
echo "   🔍 Qdrant:    http://localhost:6333/dashboard"
echo ""
echo "📖 Quick start:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Go to Documents page and upload a PDF"
echo "   3. Process the document and ask questions!"
echo ""