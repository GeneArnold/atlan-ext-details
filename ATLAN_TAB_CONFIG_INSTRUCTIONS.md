# 📋 Atlan Tab Configuration Instructions

## JSON Configuration for Atlan

The file `atlan-tab-config.json` contains the configuration that needs to be added to Atlan's LaunchDarkly feature flag to register your external tab.

## 🎯 What to Send to Atlan Admin

### 1. Your Render URL
Once deployed to Render, you'll get a URL like:
- `https://atlan-external-tab.onrender.com` (replace with your actual URL)

### 2. The Configuration JSON

**IMPORTANT**: Update the `iframe_url` and `allowed_origins` with your actual Render URL!

```json
{
  "external-details-tab": {
    "display_name": "External Details",
    "iframe_url": "https://YOUR-APP-NAME.onrender.com",
    "allowed_origins": [
      "https://YOUR-APP-NAME.onrender.com",
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

## 📝 Configuration Explained

### Core Settings
- **`display_name`**: "External Details" - The tab label users will see
- **`iframe_url`**: Your Render deployment URL
- **`allowed_origins`**: URLs allowed for postMessage communication (security)
- **`icon`**: "Analytics" - Icon from Atlan's icon set
- **`description`**: What appears in tooltips/navigation

### Placement Configuration
- **`slot`**: "asset-profile-tab" - Adds a tab to asset detail pages
- **`assetTypes`**: List of asset types where the tab appears

Currently configured to show on:
- Tables, Views, Columns (database objects)
- Database, Schema (containers)
- Glossary terms and categories
- Connections

## 🚀 Steps for Atlan Admin

1. **Deploy to Render first** and get your URL
2. **Update the JSON** with your actual Render URL
3. **Send to Atlan Admin** with this message:

> Please add this external tab configuration to the LaunchDarkly feature flag `external-iframe-tabs` for tenant `fs3.atlan.com`:
>
> - App ID: `external-details-tab`
> - Render URL: `https://YOUR-APP-NAME.onrender.com`
> - OAuth Redirect URIs to add:
>   - `https://YOUR-APP-NAME.onrender.com`
>   - `https://YOUR-APP-NAME.onrender.com/*`
>
> Configuration JSON attached.

## 🔑 OAuth Configuration

The Atlan admin also needs to:

1. **Register OAuth redirect URIs** in Keycloak:
   - Your Render URL
   - Your Render URL with wildcard path

2. **Add to allowed origins** for CORS

## ✅ Testing After Configuration

Once configured in Atlan:

1. Navigate to any Table, View, or Column in Atlan
2. Look for "External Details" tab
3. Click the tab
4. Should see:
   - User authentication info
   - Asset GUID
   - Asset description

## 🎨 Customization Options

You can modify the JSON to:

### Show on Different Asset Types
```json
"assetTypes": ["Table", "View"]  // Only tables and views
```

### Add to Navigation
```json
"render_at": [
  {
    "slot": "nav-tab"  // Adds to left navigation
  }
]
```

### Multiple Locations
```json
"render_at": [
  {
    "slot": "asset-profile-tab",
    "when": { "assetTypes": ["Table"] }
  },
  {
    "slot": "nav-tab"
  }
]
```

## 📌 Important Notes

1. **LaunchDarkly Config**: This is managed by Atlan team, not self-service (as of March 2026)
2. **Testing**: Can be tested on staging tenant first
3. **Icon Options**: Analytics, Database, Folder, Tag, User, Settings, etc.
4. **App ID**: Must be unique across the tenant (we use `external-details-tab`)

## 🐛 Troubleshooting

If the tab doesn't appear:
- Check LaunchDarkly flag is active
- Verify asset type matches configuration
- Check browser console for errors
- Ensure OAuth redirect URIs are registered

## 📞 Contact

Work with your Atlan Customer Success Manager or Support team to get this configured.