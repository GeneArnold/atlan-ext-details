#!/usr/bin/env python
"""
Simple test script to verify the training example setup.
Run this to check if all dependencies are installed correctly.
"""

import sys
print("="*60)
print("ATLAN TRAINING EXAMPLE - SETUP TEST")
print("="*60)

# Test Python version
print(f"\n✓ Python version: {sys.version}")

# Test imports
try:
    import flask
    print(f"✓ Flask installed: {flask.__version__}")
except ImportError:
    print("✗ Flask not installed - run: pip install flask")

try:
    import flask_cors
    print("✓ Flask-CORS installed")
except ImportError:
    print("✗ Flask-CORS not installed - run: pip install flask-cors")

try:
    import pyatlan
    print("✓ pyatlan installed")
except ImportError:
    print("✗ pyatlan not installed - run: pip install pyatlan")

try:
    import dotenv
    print("✓ python-dotenv installed")
except ImportError:
    print("✗ python-dotenv not installed (optional)")

print("\n" + "="*60)
print("QUICK START COMMANDS:")
print("="*60)
print("\n1. Start the backend:")
print("   python backend.py")
print("\n2. Start the frontend (in another terminal):")
print("   python -m http.server 8000")
print("\n3. Open in browser:")
print("   http://localhost:8000")
print("\n" + "="*60)