"""
Atlan External Tab - Production App for Render Deployment
This combines the frontend and backend into a single Flask application
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from pyatlan.client.atlan import AtlanClient
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
    Fetch asset details from Atlan using pyatlan SDK
    """
    logger.info(f"Fetching asset: {guid}")

    try:
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid authorization token'}), 401

        token = auth_header.replace('Bearer ', '')

        # Initialize Atlan client
        client = AtlanClient(
            base_url=ATLAN_BASE_URL,
            api_key=token
        )

        # Fetch asset
        asset = client.asset.get_by_guid(
            guid=guid,
            min_ext_info=False,
            ignore_relationships=False
        )

        if not asset:
            return jsonify({'error': f'Asset not found: {guid}'}), 404

        # Return asset details
        asset_details = {
            'guid': asset.guid,
            'name': asset.name,
            'type_name': asset.type_name,
            'qualified_name': asset.qualified_name,
            'description': asset.user_description or asset.description or 'No description available',
            'created_by': asset.created_by,
            'modified_by': asset.modified_by,
            'certificate_status': asset.certificate_status
        }

        # Add type-specific fields if available
        if hasattr(asset, 'database_name'):
            asset_details['database_name'] = asset.database_name
        if hasattr(asset, 'schema_name'):
            asset_details['schema_name'] = asset.schema_name
        if hasattr(asset, 'table_name'):
            asset_details['table_name'] = asset.table_name

        logger.info(f"Successfully fetched asset: {asset.name}")
        return jsonify(asset_details)

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