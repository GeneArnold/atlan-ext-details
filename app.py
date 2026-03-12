"""
Atlan External Tab - Production App for Render Deployment
This combines the frontend and backend into a single Flask application
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import logging
import os

# Create Flask app
app = Flask(__name__)

# Enable CORS for Atlan domains
CORS(app, origins=[
    'https://*.atlan.com',
    'https://fs3.atlan.com',
    'https://partner-sandbox.atlan.com',
    'http://localhost:*'  # For development only
])

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Configuration from environment
ATLAN_BASE_URL = os.getenv('ATLAN_BASE_URL', 'https://fs3.atlan.com')
PORT = int(os.getenv('PORT', 10000))  # Render uses PORT env variable

# ============================================
# FRONTEND ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check for Render"""
    return jsonify({'status': 'healthy', 'service': 'atlan-external-tab'})

# ============================================
# API ROUTES
# ============================================

@app.route('/api/health')
def api_health():
    """API health check"""
    logger.info("API health check requested")
    return jsonify({
        'status': 'healthy',
        'message': 'Atlan external tab API is running',
        'atlan_url': ATLAN_BASE_URL
    })

@app.route('/api/asset/<guid>')
def get_asset(guid):
    """
    Fetch asset details from Atlan using REST API with OAuth Bearer token
    """
    logger.info(f"Fetching asset: {guid}")

    try:
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid authorization token'}), 401

        token = auth_header.replace('Bearer ', '')

        # Use Atlan REST API directly with Bearer token
        # Atlan API endpoint for fetching asset by GUID
        api_url = f"{ATLAN_BASE_URL}/api/meta/entity/guid/{guid}"

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        logger.info(f"Calling Atlan API: {api_url}")
        response = requests.get(api_url, headers=headers)

        if response.status_code == 404:
            return jsonify({'error': f'Asset not found: {guid}'}), 404
        elif response.status_code == 401:
            return jsonify({'error': 'Authentication failed - token may be invalid'}), 401
        elif response.status_code != 200:
            logger.error(f"API returned status {response.status_code}: {response.text}")
            return jsonify({'error': f'API error: {response.status_code}'}), response.status_code

        # Parse the response
        asset_data = response.json()

        if 'entity' in asset_data:
            entity = asset_data['entity']
        else:
            entity = asset_data

        # Extract asset details from API response
        attributes = entity.get('attributes', {})

        asset_details = {
            'guid': entity.get('guid', guid),
            'name': attributes.get('name') or entity.get('displayText') or 'Unknown',
            'type_name': entity.get('typeName', 'Unknown'),
            'qualified_name': attributes.get('qualifiedName', 'N/A'),
            'description': (
                attributes.get('userDescription') or
                attributes.get('description') or
                entity.get('meanings', [{}])[0].get('displayText', 'No description available') if entity.get('meanings') else
                'No description available'
            ),
            'created_by': entity.get('createdBy', 'Unknown'),
            'modified_by': entity.get('updatedBy', 'Unknown'),
            'certificate_status': attributes.get('certificateStatus', 'N/A')
        }

        # Add type-specific fields if available
        if 'databaseName' in attributes:
            asset_details['database_name'] = attributes['databaseName']
        if 'schemaName' in attributes:
            asset_details['schema_name'] = attributes['schemaName']
        if 'tableName' in attributes:
            asset_details['table_name'] = attributes['tableName']

        logger.info(f"Successfully fetched asset: {asset_details['name']}")
        return jsonify(asset_details)

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({'error': f'Failed to connect to Atlan API: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error fetching asset: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    logger.info(f"Starting Atlan External Tab on port {PORT}")
    logger.info(f"Atlan URL: {ATLAN_BASE_URL}")
    app.run(host='0.0.0.0', port=PORT, debug=False)