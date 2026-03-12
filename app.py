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

@app.route('/api/asset/<guid>/debug')
def debug_asset(guid):
    """
    Debug endpoint - returns raw API response to find description field
    """
    logger.info(f"DEBUG: Fetching raw asset data for: {guid}")

    try:
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid authorization token'}), 401

        token = auth_header.replace('Bearer ', '')

        # Call Atlan API
        api_url = f"{ATLAN_BASE_URL}/api/meta/entity/guid/{guid}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            return jsonify({'error': f'API error: {response.status_code}'}), response.status_code

        # Return the raw response for debugging
        return response.json()

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

        # Debug logging to find description
        logger.info("=== DEBUG: Looking for description ===")
        logger.info(f"Attribute keys: {list(attributes.keys())}")

        # Log ALL attributes to find where description is hiding
        for key, value in attributes.items():
            if value and isinstance(value, str) and len(value) > 20:
                logger.info(f"Attribute {key}: {value[:100]}...")

        # Check all possible description fields
        desc_fields = ['description', 'userDescription', 'businessDescription', 'comment', 'remarks']
        for field in desc_fields:
            if field in attributes:
                logger.info(f"Found {field}: {attributes[field][:100] if attributes[field] else 'None'}")

        # Check relationship attributes for readme
        rel_attrs = entity.get('relationshipAttributes', {})
        if 'readme' in rel_attrs:
            logger.info(f"Found readme in relationships: {rel_attrs['readme']}")

        logger.info("=== END DEBUG ===")

        # Get description - userDescription is the field we need!
        description = attributes.get('userDescription')
        logger.info(f"userDescription field: {description[:100] if description else 'None'}")

        if not description:
            description = attributes.get('description')
        if not description:
            description = attributes.get('comment')
        if not description:
            description = attributes.get('remarks')
        if not description:
            meanings = entity.get('meanings', [])
            if meanings and len(meanings) > 0:
                description = meanings[0].get('displayText', 'No description available')
            else:
                description = 'No description available'

        asset_details = {
            'guid': entity.get('guid', guid),
            'name': attributes.get('name') or entity.get('displayText') or 'Unknown',
            'type_name': entity.get('typeName', 'Unknown'),
            'qualified_name': attributes.get('qualifiedName', 'N/A'),
            'description': description,
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