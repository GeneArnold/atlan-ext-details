#!/bin/bash

# Quick test script to verify backend is running
echo "Testing Atlan Training Backend..."
echo ""

# Test health endpoint
echo "Testing health endpoint..."
response=$(curl -s http://localhost:5000/api/health)

if [ $? -eq 0 ]; then
    echo "✅ Backend is running!"
    echo "Response: $response"
else
    echo "❌ Backend is not running. Please start it with:"
    echo "   source venv/bin/activate"
    echo "   python backend.py"
fi

echo ""