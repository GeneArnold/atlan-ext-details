#!/bin/bash

# Atlan Custom Tab - Quick Setup Script
# This script helps you quickly set up a new Atlan tab project

echo "🚀 Atlan Custom Tab Quick Setup"
echo "================================"
echo ""

# Ask for project type
echo "What type of project do you want to create?"
echo "1) Simple HTML tab (no backend)"
echo "2) Python Flask app with API"
echo "3) OAuth-enabled application"
echo ""
read -p "Enter choice [1-3]: " choice

# Ask for project name
read -p "Enter project name (e.g., my-atlan-tab): " PROJECT_NAME

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

case $choice in
    1)
        echo "📄 Creating simple HTML tab..."
        cp ../simple-tab-template.html index.html
        cp ../postmessage-implementation.js postmessage.js

        cat > README.md << 'EOF'
# Simple Atlan Tab

## Local Testing
Open index.html in a browser with:
- `?test=true` - Simulates Atlan messages
- `?debug=true` - Shows debug panel

## Deployment
Upload to any static hosting service (GitHub Pages, Netlify, etc.)

## Customization
Edit the `loadAsset()` function in index.html to add your logic.
EOF

        echo "✅ Simple HTML tab created!"
        echo "📝 Edit index.html to customize your tab"
        echo "🧪 Test with: open index.html?test=true"
        ;;

    2)
        echo "🐍 Creating Python Flask app..."

        # Create app.py
        cat > app.py << 'EOF'
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config')
def config():
    """Check if app is configured"""
    return jsonify({
        'configured': bool(os.getenv('ATLAN_API_KEY'))
    })

@app.route('/api/asset/<guid>')
def get_asset(guid):
    """Get asset details"""
    # TODO: Add your asset loading logic here
    return jsonify({
        'success': True,
        'id': guid,
        'name': 'Sample Asset',
        'description': 'Add your logic here'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
EOF

        # Create templates directory
        mkdir -p templates
        cp ../simple-tab-template.html templates/index.html

        # Create requirements.txt
        cp ../requirements-example.txt requirements.txt

        # Create .env template
        cat > .env.example << 'EOF'
# Atlan Configuration
ATLAN_BASE_URL=https://partner-sandbox.atlan.com
ATLAN_API_KEY=your-api-key-here

# Add your other environment variables here
EOF

        # Create Procfile for Render
        cp ../Procfile-example Procfile

        # Create Python version file
        cp ../.python-version-example .python-version

        # Create .gitignore
        cat > .gitignore << 'EOF'
.env
*.pyc
__pycache__/
venv/
.DS_Store
EOF

        cat > README.md << 'EOF'
# Flask Atlan Tab

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your credentials

## Local Development
```bash
python app.py
```
Visit http://localhost:5000?test=true

## Deployment to Render
1. Push to GitHub
2. Connect to Render
3. Add environment variables
4. Deploy!
EOF

        echo "✅ Flask app created!"
        echo "📝 Next steps:"
        echo "   1. python -m venv venv"
        echo "   2. source venv/bin/activate"
        echo "   3. pip install -r requirements.txt"
        echo "   4. cp .env.example .env"
        echo "   5. python app.py"
        ;;

    3)
        echo "🔐 Creating OAuth-enabled app..."
        cp -r ../oauth-example/* .

        cat > README.md << 'EOF'
# OAuth-Enabled Atlan Tab

## Quick Start
```bash
docker-compose up --build
```
Visit http://localhost:3000

## Configuration
Edit `.env` with your OAuth credentials

## Testing
Click "Start OAuth Flow" to test authentication
EOF

        echo "✅ OAuth app created!"
        echo "📝 Next steps:"
        echo "   1. Edit .env with your OAuth credentials"
        echo "   2. docker-compose up --build"
        echo "   3. Visit http://localhost:3000"
        ;;

    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Project '$PROJECT_NAME' created successfully!"
echo "📂 cd $PROJECT_NAME to get started"
echo ""
echo "⚠️  IMPORTANT REMINDERS:"
echo "   - Set up message listeners IMMEDIATELY (not on window.load)"
echo "   - Use 'undefined' for uninitialized state (not 'false')"
echo "   - Always validate message origins"
echo "   - Never use '*' for postMessage targetOrigin"
echo "   - Test in incognito mode with cleared cache"
echo ""
echo "📚 See README.md in the parent directory for detailed documentation"