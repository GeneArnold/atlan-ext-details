"""
ATLAN EXTERNAL TAB TRAINING EXAMPLE - BACKEND
==============================================
This Python backend demonstrates how to:
1. Receive authentication tokens from the frontend
2. Use pyatlan SDK to fetch asset details
3. Return asset information to the frontend

Requirements:
- Flask: Web framework for Python
- pyatlan: Official Atlan Python SDK
- flask-cors: Handle CORS for frontend communication
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pyatlan.client.atlan import AtlanClient
from pyatlan.model.assets import Asset
import logging
import os

# ============================================
# SETUP AND CONFIGURATION
# ============================================

# Create Flask application
app = Flask(__name__)

# Enable CORS to allow frontend to communicate with backend
# In production, you would restrict this to specific origins
CORS(app, origins=['http://localhost:*', 'https://*.atlan.com'])

# Configure logging for better debugging during training
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# HELPER FUNCTIONS
# ============================================

def extract_token_from_header(auth_header):
    """
    Extract the JWT token from the Authorization header.
    Expected format: "Bearer <token>"

    Args:
        auth_header: The Authorization header value

    Returns:
        The token string or None if invalid
    """
    if not auth_header:
        return None

    parts = auth_header.split(' ')
    if len(parts) != 2 or parts[0] != 'Bearer':
        return None

    return parts[1]


def initialize_atlan_client(token):
    """
    Initialize the Atlan client with the provided JWT token.

    Args:
        token: JWT token from the frontend

    Returns:
        Configured AtlanClient instance
    """
    # IMPORTANT: In a real deployment, you would get the base_url from
    # environment variables or configuration
    base_url = os.getenv('ATLAN_BASE_URL', 'https://your-tenant.atlan.com')

    # Create client with the token from the frontend
    # The token comes from the Atlan Auth SDK in the frontend
    client = AtlanClient(
        base_url=base_url,
        api_key=token  # Using the JWT token as API key
    )

    return client


def get_asset_details_from_atlan(guid, token):
    """
    Fetch asset details from Atlan using pyatlan SDK.

    This function demonstrates the key integration point:
    - We receive a GUID from the frontend (which got it from Atlan via postMessage)
    - We use the OAuth token to authenticate
    - We fetch the actual asset details using pyatlan

    Args:
        guid: The asset GUID to fetch
        token: JWT token for authentication

    Returns:
        Dictionary containing asset details
    """
    try:
        logger.info(f"[TRAINING] Fetching asset with GUID: {guid}")

        # Initialize Atlan client with the token
        client = initialize_atlan_client(token)

        # Fetch the asset using pyatlan SDK
        # This is the core functionality - getting asset details by GUID
        asset = client.asset.get_by_guid(
            guid=guid,
            min_ext_info=False,  # Get full information
            ignore_relationships=False  # Include relationships
        )

        if not asset:
            logger.warning(f"[TRAINING] No asset found with GUID: {guid}")
            return None

        logger.info(f"[TRAINING] Found asset: {asset.name} (Type: {asset.type_name})")

        # Extract the information we want to display
        # For training purposes, we're keeping this simple
        asset_details = {
            'guid': asset.guid,
            'name': asset.name,
            'type_name': asset.type_name,
            'qualified_name': asset.qualified_name,
            'description': asset.user_description or asset.description,
            'created_by': asset.created_by,
            'created_time': str(asset.create_time) if asset.create_time else None,
            'modified_by': asset.modified_by,
            'modified_time': str(asset.update_time) if asset.update_time else None,
            'owner_users': asset.owner_users or [],
            'owner_groups': asset.owner_groups or [],
            'certificate_status': asset.certificate_status
        }

        # Add Atlan tags if present
        if asset.atlan_tags:
            asset_details['tags'] = [tag.type_name for tag in asset.atlan_tags]

        # Add type-specific details (demonstrating flexibility)
        # The pyatlan SDK returns the correct type automatically
        if hasattr(asset, 'database_name'):
            asset_details['database_name'] = asset.database_name
        if hasattr(asset, 'schema_name'):
            asset_details['schema_name'] = asset.schema_name
        if hasattr(asset, 'table_name'):
            asset_details['table_name'] = asset.table_name
        if hasattr(asset, 'column_count'):
            asset_details['column_count'] = asset.column_count
        if hasattr(asset, 'row_count'):
            asset_details['row_count'] = asset.row_count

        return asset_details

    except Exception as e:
        logger.error(f"[TRAINING] Error fetching asset: {str(e)}")
        raise


# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the backend is running.
    Useful for testing the backend independently.
    """
    logger.info("[TRAINING] Health check requested")
    return jsonify({
        'status': 'healthy',
        'message': 'Atlan training backend is running'
    })


@app.route('/api/asset/<guid>', methods=['GET'])
def get_asset(guid):
    """
    Main endpoint to fetch asset details.

    This endpoint:
    1. Receives the asset GUID in the URL
    2. Extracts the JWT token from the Authorization header
    3. Uses pyatlan to fetch asset details
    4. Returns the details to the frontend

    URL Parameters:
        guid: The asset GUID to fetch

    Headers:
        Authorization: Bearer <token>

    Returns:
        JSON object with asset details or error message
    """
    logger.info(f"[TRAINING] Received request for asset: {guid}")

    try:
        # Extract the token from Authorization header
        auth_header = request.headers.get('Authorization')
        token = extract_token_from_header(auth_header)

        if not token:
            logger.warning("[TRAINING] No valid token provided")
            return jsonify({
                'error': 'No valid authorization token provided'
            }), 401

        # Fetch asset details using pyatlan
        asset_details = get_asset_details_from_atlan(guid, token)

        if not asset_details:
            return jsonify({
                'error': f'Asset not found: {guid}'
            }), 404

        logger.info(f"[TRAINING] Successfully fetched asset: {asset_details['name']}")
        return jsonify(asset_details), 200

    except Exception as e:
        logger.error(f"[TRAINING] Error processing request: {str(e)}")
        return jsonify({
            'error': f'Failed to fetch asset details: {str(e)}'
        }), 500


@app.route('/api/test-asset', methods=['POST'])
def test_asset_fetch():
    """
    Test endpoint for development - allows testing with a hardcoded token.
    DO NOT USE IN PRODUCTION!

    This endpoint is useful for testing the pyatlan integration
    without needing the full frontend authentication flow.
    """
    data = request.get_json()
    guid = data.get('guid')
    token = data.get('token')  # In production, never accept tokens in request body!

    if not guid or not token:
        return jsonify({'error': 'Missing guid or token'}), 400

    try:
        asset_details = get_asset_details_from_atlan(guid, token)
        return jsonify(asset_details), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == '__main__':
    """
    Start the Flask development server.

    For training purposes, we're using Flask's built-in server.
    In production, you would use a proper WSGI server like Gunicorn.
    """
    print("\n" + "="*60)
    print("ATLAN EXTERNAL TAB TRAINING BACKEND")
    print("="*60)
    print("\nStarting Flask server...")
    print("Backend will be available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  - GET  /api/health        -> Health check")
    print("  - GET  /api/asset/<guid>  -> Fetch asset details")
    print("  - POST /api/test-asset    -> Test endpoint (dev only)")
    print("\nMake sure to:")
    print("  1. Set ATLAN_BASE_URL environment variable")
    print("  2. Have pyatlan and flask installed")
    print("  3. Run the frontend on a different port")
    print("\n" + "="*60 + "\n")

    # Run the Flask development server
    app.run(
        host='0.0.0.0',  # Accept connections from any host
        port=5000,        # Run on port 5000
        debug=True        # Enable debug mode for training
    )