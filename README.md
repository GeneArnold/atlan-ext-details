# Atlan External Details Tab

A production-ready external tab for Atlan that displays asset information and demonstrates OAuth integration.

**Live URL:** https://atlan-ext-details.onrender.com
**Target Atlan:** https://fs3.atlan.com

## 🎯 What This Does

This external tab integrates into Atlan's asset profile pages and displays:
1. **User Information** - Shows the authenticated user's details (proves OAuth is working)
2. **Asset GUID** - Displays the current asset's unique identifier (proves iframe communication)
3. **Asset Description** - Fetches and shows the asset's description using pyatlan SDK (proves API integration)

## 🚀 Current Status

✅ **Deployed to Render** at https://atlan-ext-details.onrender.com
⏳ **Awaiting Configuration** - Needs to be added to Atlan's LaunchDarkly feature flag

## 📦 Production Files (What Actually Runs)

```
/
├── app.py                    # Flask application (serves frontend and API)
├── templates/
│   └── index.html           # Frontend UI with Atlan Auth SDK
├── requirements.txt         # Python dependencies
├── runtime.txt             # Python version (3.11.10) - CRITICAL!
├── render.yaml             # Render.com configuration
├── Procfile               # Web server configuration
└── atlan-tab-config.json  # Configuration for Atlan admin
```

## 🔧 For Atlan Administrators

### Configuration Required

The app is deployed and running. To enable it in Atlan, add this configuration to the LaunchDarkly feature flag `external-iframe-tabs` for `fs3.atlan.com`:

```json
{
  "external-details-tab": {
    "display_name": "External Details",
    "iframe_url": "https://atlan-ext-details.onrender.com",
    "allowed_origins": [
      "https://atlan-ext-details.onrender.com",
      "https://*.onrender.com"
    ],
    "icon": "Analytics",
    "description": "Displays asset details with user authentication info",
    "render_at": [
      {
        "slot": "asset-profile-tab",
        "when": {
          "assetTypes": [
            "Table", "View", "MaterialisedView", "Column",
            "Database", "Schema", "AtlasGlossary",
            "AtlasGlossaryTerm", "AtlasGlossaryCategory", "Connection"
          ]
        }
      }
    ]
  }
}
```

### OAuth Setup Required

Register these redirect URIs in Keycloak:
- `https://atlan-ext-details.onrender.com`
- `https://atlan-ext-details.onrender.com/*`

## 🏗️ How It Works

1. **User clicks "External Details" tab** in any asset profile page in Atlan
2. **Atlan loads the app** in an iframe from Render
3. **Authentication happens automatically** via Atlan Auth SDK
4. **App displays**:
   - User details from OAuth token
   - Asset GUID from iframe context
   - Asset description from pyatlan API call

## 🔍 Testing the Deployment

### Health Check
```bash
curl https://atlan-ext-details.onrender.com/health
```

Expected: `{"status": "healthy", "service": "atlan-external-tab"}`

### After Configuration in Atlan
1. Navigate to any Table, Column, or Glossary term
2. Look for "External Details" tab
3. Click to see the information display

## ⚠️ Important Notes

### OAuth Requirements
- **Cannot test locally** - OAuth redirect URIs must be registered
- Must be deployed to public URL for authentication to work

### Python Version
- **Must use Python 3.11.10** (specified in `runtime.txt`)
- Newer versions cause pydantic compilation failures

### Render Deployment
- Free tier spins down after inactivity
- First request after idle takes ~30 seconds
- Logs available in Render dashboard

## 📁 Other Files in Repository

### Documentation
- `atlan-tab-config.json` - Configuration for Atlan admin
- `MESSAGE_FOR_ATLAN_ADMIN.md` - Pre-written setup message
- `DEPLOY_TO_RENDER.md` - Deployment instructions

### Legacy Code (Reference Only)
- `/training-example/` - Educational code (doesn't work locally due to OAuth)
- `/oauth-example/` - Complex OAuth implementation (not used in production)
- `simple-tab-template.html` - Standalone example with test mode

## 🔄 Making Changes

1. Edit files locally
2. Push to GitHub: `git push`
3. Deploy on Render: "Manual Deploy" in dashboard
4. Test health endpoint

---

**Repository:** https://github.com/GeneArnold/atlan-ext-details
**Live App:** https://atlan-ext-details.onrender.com
**Target:** https://fs3.atlan.com