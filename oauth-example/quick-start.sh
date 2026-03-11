#!/bin/bash

echo "================================================"
echo "  Atlan OAuth Example - Quick Start"
echo "================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Creating from template..."
    cp .env.example .env
    echo "Please edit the .env file with your OAuth credentials."
    exit 1
fi

echo "✓ Configuration file found"
echo ""

# Check if OAuth credentials are configured
if grep -q "oauth-client-2ecb7cc0-08d1-43f3-9159-fceadbf0d739" .env; then
    echo "✓ OAuth credentials configured"
else
    echo "⚠️  OAuth credentials may not be configured"
    echo "   Make sure your .env file has the correct Client ID and Secret"
fi

echo ""
echo "Starting the OAuth example application..."
echo ""

# Build and start the container
docker-compose up --build -d

# Wait for the service to be ready
echo "Waiting for service to start..."
sleep 3

# Check if the service is running
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo ""
    echo "================================================"
    echo "  ✅ Application is running!"
    echo "================================================"
    echo ""
    echo "Open your browser and go to:"
    echo "  → http://localhost:3000"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To stop the application:"
    echo "  docker-compose down"
    echo ""
    echo "To test the API token directly:"
    echo "  docker-compose exec oauth-app node test-api-token.js"
    echo ""
else
    echo ""
    echo "⚠️  Service might not be ready yet. Check logs with:"
    echo "  docker-compose logs"
    echo ""
fi