#!/bin/bash

# Issue Tracker API - Quick Start Script

set -e

echo "🎯 Issue Tracker API - Quick Start"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update if needed."
fi

echo ""
echo "🚀 Starting services with Docker Compose..."
docker-compose up -d

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

echo ""
echo "📦 Running database migrations..."
docker-compose exec -T app alembic upgrade head

echo ""
echo "✅ Issue Tracker API is now running!"
echo ""
echo "📍 API URL: http://localhost:5000"
echo "📍 Health Check: http://localhost:5000/api/v1/health"
echo ""
echo "🧪 To run tests:"
echo "   docker-compose exec app pytest"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
echo ""
echo "📚 See README.md for more information and API documentation."
