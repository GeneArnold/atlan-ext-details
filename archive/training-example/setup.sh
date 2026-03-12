#!/bin/bash

# Setup script for Atlan External Tab Training Example
echo "=========================================="
echo "Atlan Training Example - Setup Script"
echo "=========================================="
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start developing:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start the backend:"
echo "   python backend.py"
echo ""
echo "3. In another terminal, start the frontend:"
echo "   python -m http.server 8000"
echo ""
echo "4. Open in browser:"
echo "   http://localhost:8000"
echo ""