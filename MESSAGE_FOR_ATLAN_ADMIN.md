# Message to Send to Atlan Admin

## Copy and Send This Message:

---

Hi Team,

Please add our new external tab to the LaunchDarkly feature flag `external-iframe-tabs` for tenant `fs3.atlan.com`.

**App Details:**
- **App ID:** `external-details-tab`
- **Display Name:** External Details
- **Render URL:** https://atlan-ext-details.onrender.com
- **Description:** Displays asset details with user authentication info

**OAuth Redirect URIs to Register in Keycloak:**
- https://atlan-ext-details.onrender.com
- https://atlan-ext-details.onrender.com/*

**Configuration JSON:**
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
            "Table",
            "View",
            "MaterialisedView",
            "Column",
            "Database",
            "Schema",
            "AtlasGlossary",
            "AtlasGlossaryTerm",
            "AtlasGlossaryCategory",
            "Connection"
          ]
        }
      }
    ]
  }
}
```

The app is already deployed and running on Render. Once you configure the LaunchDarkly flag and OAuth settings, the external tab should appear on all asset profile pages for the specified asset types.

Please let me know if you need any additional information or have questions about the configuration.

Thank you!

---

## Additional Notes for Admin:

1. **Testing URL:** https://atlan-ext-details.onrender.com/health (should return `{"status": "healthy", "service": "atlan-external-tab"}`)

2. **What the tab does:**
   - Shows authenticated user information
   - Displays the current asset's GUID
   - Fetches and displays the asset's description using pyatlan SDK

3. **Security:**
   - Uses Atlan Auth SDK for OAuth
   - All postMessage communication uses explicit origins
   - Tokens stored in memory only

4. **Asset Types Configured:**
   - Database objects (Table, View, MaterialisedView, Column)
   - Schema containers (Database, Schema)
   - Glossary items (AtlasGlossary, AtlasGlossaryTerm, AtlasGlossaryCategory)
   - Connections

5. **Deployment:**
   - Hosted on Render.com
   - Auto-scales based on usage
   - Logs available in Render dashboard