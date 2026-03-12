# Atlan External Tab Integration - Teaching Guide

## Introduction

This guide teaches you how to build an external tab integration for Atlan that:
1. **Authenticates** users via OAuth 2.0
2. **Communicates** with the Atlan parent window via postMessage
3. **Retrieves** and displays asset information using Atlan's REST API

## Prerequisites

- Basic understanding of HTML, JavaScript, and Python
- Familiarity with OAuth 2.0 concepts
- Access to an Atlan instance (e.g., https://fs3.atlan.com)
- A deployment platform (we use Render.com)

## Architecture Overview

```
┌──────────────────────────────────────┐
│         Atlan Platform               │
│  ┌──────────────────────────────┐   │
│  │     Asset Details Page       │   │
│  │  ┌────────────────────────┐  │   │
│  │  │   External Tab iframe  │  │   │  ← Your App
│  │  │   (Your Application)   │  │   │
│  │  └────────────────────────┘  │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

## Part 1: Understanding the OAuth Flow

### Traditional OAuth vs Atlan Auth SDK

**Traditional OAuth (200+ lines of code):**
- Build authorization URL manually
- Handle redirect and token exchange
- Manage PKCE flow
- Handle token refresh

**Atlan Auth SDK (10 lines of code):**
```javascript
const atlan = new AtlanAuth({
    origin: 'https://fs3.atlan.com',
    onReady: (context) => {
        // You're authenticated!
    },
    onError: (error) => {
        // Handle errors
    }
});
atlan.init();
```

The SDK handles everything automatically, including:
- OAuth 2.0 with PKCE
- Token management
- Iframe communication
- Automatic token refresh

## Part 2: The Three Key Integrations

### 1. OAuth Authentication (Proves Authentication Works)

The SDK provides user information after successful authentication:

```javascript
onReady: (context) => {
    const user = context.user;
    // In standalone mode: Full user details with permissions
    // In embedded mode: Basic profile (id, username, email, name)
}
```

### 2. PostMessage Communication (Proves Iframe Integration Works)

When embedded in Atlan, the app receives the current asset's GUID via postMessage:

```javascript
// Critical: Add this BEFORE initializing the SDK
window.addEventListener('message', (event) => {
    if (event.origin !== ATLAN_INSTANCE_URL) return;

    if (event.data?.type === 'ATLAN_AUTH_CONTEXT') {
        // Capture the asset GUID
        assetGuid = event.data.payload?.page?.params?.id;
    }
});
```

**Why before SDK initialization?**
The SDK processes and strips the page context from messages. By listening first, we capture the raw data.

### 3. REST API Integration (Proves Backend Integration Works)

Use the OAuth token as a Bearer token for API calls:

```python
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
response = requests.get(f"{ATLAN_BASE_URL}/api/meta/entity/guid/{guid}", headers=headers)
```

## Part 3: Implementation Step-by-Step

### Step 1: Create the Frontend (templates/index.html)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Atlan External Details Tab</title>
</head>
<body>
    <div id="content">
        <div class="loading">Loading...</div>
    </div>

    <!-- Load Atlan Auth SDK -->
    <script src="https://unpkg.com/@atlanhq/atlan-auth@latest/dist/atlan-auth.umd.min.js"></script>

    <script>
        const { AtlanAuth } = window.AtlanAuthSDK;
        const ATLAN_INSTANCE_URL = 'https://fs3.atlan.com';

        let assetGuidFromMessage = null;

        // Step 1: Capture asset GUID from raw message
        window.addEventListener('message', (event) => {
            if (event.origin !== ATLAN_INSTANCE_URL) return;

            if (event.data?.type === 'ATLAN_AUTH_CONTEXT') {
                if (event.data.payload?.page?.params?.id) {
                    assetGuidFromMessage = event.data.payload.page.params.id;
                }
            }
        });

        // Step 2: Initialize SDK
        const atlan = new AtlanAuth({
            origin: ATLAN_INSTANCE_URL,
            onReady: async (context) => {
                // Step 3: Display user info
                displayUserInfo(context.user);

                // Step 4: Fetch asset details if in embedded mode
                if (context.mode === 'embedded' && assetGuidFromMessage) {
                    await fetchAssetDetails(assetGuidFromMessage, context.token);
                }
            },
            onError: (error) => {
                displayError(error.message);
            }
        });

        atlan.init();
    </script>
</body>
</html>
```

### Step 2: Create the Backend (app.py)

```python
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, origins=['https://*.atlan.com'])

ATLAN_BASE_URL = 'https://fs3.atlan.com'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/asset/<guid>')
def get_asset(guid):
    # Get OAuth token from header
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')

    # Call Atlan REST API
    api_url = f"{ATLAN_BASE_URL}/api/meta/entity/guid/{guid}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(api_url, headers=headers)
    data = response.json()

    # Extract asset details
    entity = data.get('entity', data)
    attributes = entity.get('attributes', {})

    return jsonify({
        'name': attributes.get('name'),
        'description': attributes.get('userDescription'),  # Note: userDescription field
        'type_name': entity.get('typeName'),
        'qualified_name': attributes.get('qualifiedName')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
```

### Step 3: Deploy to Render.com

1. **Create requirements.txt:**
```
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
gunicorn==21.2.0
```

2. **Create runtime.txt (CRITICAL):**
```
python-3.11.10
```
This prevents pydantic compilation errors with newer Python versions.

3. **Configure Render:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

### Step 4: Configure in Atlan

Create the external tab configuration:
```json
{
  "id": "external-details-tab",
  "name": "External Details",
  "url": "https://your-app.onrender.com",
  "groups": ["asset-profile-tab"],
  "supportedAssetTypes": ["Table", "Column", "Database", "Schema"],
  "iconUrl": "https://your-app.onrender.com/icon.png"
}
```

## Part 4: Common Pitfalls and Solutions

### Pitfall 1: Asset GUID Not Available

**Problem:** The SDK strips page context in embedded mode.

**Solution:** Capture from raw postMessage BEFORE SDK initialization:
```javascript
window.addEventListener('message', (event) => {
    // This runs BEFORE the SDK processes the message
    if (event.data?.type === 'ATLAN_AUTH_CONTEXT') {
        assetGuid = event.data.payload?.page?.params?.id;
    }
});
```

### Pitfall 2: OAuth Token Doesn't Work with pyatlan SDK

**Problem:** The pyatlan SDK expects an API key, not an OAuth token.

**Solution:** Use the REST API directly with Bearer token:
```python
# DON'T use pyatlan SDK
# from pyatlan.client.atlan import AtlanClient

# DO use REST API
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(api_url, headers=headers)
```

### Pitfall 3: Description Field Not Found

**Problem:** Description stored in `userDescription`, not `description`.

**Solution:** Check the correct field:
```python
description = attributes.get('userDescription')  # NOT 'description'
```

### Pitfall 4: Different Data in Standalone vs Embedded

**Problem:** User object structure differs between modes.

**Solution:** Handle both cases:
```javascript
const userId = user?.userId || user?.id;  // Different field names
const email = user?.email || user?.username;  // Email location varies
```

## Part 5: Testing Your Integration

### Local Testing Limitations
- OAuth redirect URIs must be pre-registered
- Atlan won't redirect to localhost
- Solution: Deploy directly to production URL

### Testing in Atlan
1. Install your external tab via LaunchDarkly feature flag
2. Navigate to an asset page
3. Click your external tab
4. Verify:
   - User information displays
   - Asset GUID is captured
   - Asset details load from API

### Debugging Tips

Add minimal logging to track the flow:
```javascript
console.log('[ATLAN] Mode:', mode, '| Asset GUID:', assetGuid || 'N/A');
```

Check browser DevTools:
- Network tab: Verify API calls
- Console: Check for errors
- Application > Frames: Inspect iframe context

## Part 6: Security Considerations

### Always Validate Origin
```javascript
if (event.origin !== ATLAN_INSTANCE_URL) return;
```

### Use CORS Properly
```python
CORS(app, origins=['https://*.atlan.com'])  # Only allow Atlan domains
```

### Token Management
- Never store tokens in localStorage or cookies
- Keep tokens in memory only
- Request refresh before expiry

## Part 7: Next Steps

### Enhance Your Integration
1. Add more asset types support
2. Display additional metadata fields
3. Implement asset modification capabilities
4. Add custom visualizations

### Advanced Features
- Use Atlan's GraphQL API for complex queries
- Implement webhook listeners for real-time updates
- Add batch operations for multiple assets
- Create custom asset actions

## Conclusion

You've learned how to:
1. ✅ Authenticate users with Atlan Auth SDK
2. ✅ Capture asset context from iframe messages
3. ✅ Fetch asset data using OAuth Bearer tokens

The key insight: The Atlan Auth SDK dramatically simplifies OAuth integration, but understanding the underlying postMessage protocol is crucial for capturing asset context.

## Resources

- [Atlan Auth SDK Documentation](https://www.npmjs.com/package/@atlanhq/atlan-auth)
- [Atlan REST API Reference](https://developer.atlan.com/api)
- [OAuth 2.0 with PKCE](https://oauth.net/2/pkce/)
- [PostMessage API](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)

## Support

For issues or questions:
- Check the browser console for errors
- Verify your Atlan instance URL matches exactly
- Ensure your app is registered in Atlan's OAuth settings
- Review the IMPLEMENTATION_LEARNINGS.md for troubleshooting