# Troubleshooting Guide for Atlan External Tab

## Common Issues and Solutions

### 1. Asset GUID Not Available ✅ SOLVED

**Symptom**: Asset GUID shows "Not available (not in asset context)"

**Root Cause**: Atlan Auth SDK strips page context in embedded mode

**Solution**:
```javascript
// Add raw postMessage listener BEFORE SDK init
window.addEventListener('message', (event) => {
    if (event.origin !== ATLAN_INSTANCE_URL) return;
    if (event.data?.type === 'ATLAN_AUTH_CONTEXT') {
        assetGuidFromMessage = event.data.payload?.page?.params?.id;
    }
});
```

---

### 2. Backend Returns 500 Error ⚠️ CURRENT ISSUE

**Symptom**: "Failed to load asset details: Backend returned 500"

**Possible Causes**:
1. OAuth JWT token cannot be used as API key for pyatlan
2. Token lacks permissions for asset API
3. pyatlan SDK version incompatibility

**Debug Steps**:
1. Check Render logs:
   ```bash
   # In Render dashboard, check logs for actual error message
   ```

2. Test token validity:
   ```python
   # Try initializing client with different auth
   client = AtlanClient(
       base_url=ATLAN_BASE_URL,
       api_key=token  # This might be the issue
   )
   ```

**Potential Solutions**:
- Use a service account token instead of OAuth token
- Use Atlan's REST API directly instead of pyatlan SDK
- Check if token needs special scopes/permissions

---

### 3. User Fields Missing

**Symptom**: Some user fields show "N/A"

**Root Cause**: Different data structures in standalone vs embedded mode

**Solution**: Use adaptive field checking
```javascript
const userId = user?.userId || user?.id || 'N/A';
const email = user?.email || user?.username || 'N/A';
```

---

### 4. Redirect URI Error

**Symptom**: "Invalid parameter: redirect_uri" in standalone mode

**Solution**:
1. Contact Atlan admin to register URLs:
   - https://atlan-ext-details.onrender.com
   - https://atlan-ext-details.onrender.com/*

---

### 5. Tab Not Appearing in Atlan

**Symptom**: External Details tab doesn't show up

**Solution**: Ensure LaunchDarkly configuration is applied:
```json
{
  "external-details-tab": {
    "display_name": "External Details",
    "iframe_url": "https://atlan-ext-details.onrender.com",
    "allowed_origins": ["https://atlan-ext-details.onrender.com"],
    "render_at": [{
      "slot": "asset-profile-tab",
      "when": {
        "assetTypes": ["Table", "Column", ...]
      }
    }]
  }
}
```

---

## Debugging Tools

### Browser Console Commands

```javascript
// Check if SDK is loaded
console.log(window.AtlanAuthSDK);

// Check auth context
console.log(authContext);

// Check captured asset GUID
console.log(assetGuidFromMessage);

// Monitor all postMessages
window.addEventListener('message', (e) => console.log('Message:', e));
```

### Network Tab Checks

1. Check `/api/asset/{guid}` request
2. Verify Authorization header has `Bearer {token}`
3. Check response for actual error message

### Render Dashboard

1. Go to https://dashboard.render.com
2. Select `atlan-external-tab` service
3. Click "Logs" tab
4. Look for Python error messages

---

## Quick Fixes

### Force Refresh
```javascript
// Clear cache and reload
location.reload(true);
```

### Manual Token Test
```javascript
// In browser console
fetch('/api/asset/test-guid', {
    headers: {
        'Authorization': `Bearer ${authContext.token}`
    }
}).then(r => r.json()).then(console.log);
```

### Check SDK Version
```javascript
// Ensure using latest SDK
console.log(document.querySelector('script[src*="atlan-auth"]').src);
```

---

## Contact for Help

- **Atlan Support**: For SDK issues, OAuth configuration
- **Render Support**: For deployment, environment variables
- **Repository**: https://github.com/GeneArnold/atlan-ext-details
- **Documentation**: See IMPLEMENTATION_LEARNINGS.md

---

## Known Limitations

1. **OAuth Token as API Key**: May not work with pyatlan SDK
2. **Data Structure Differences**: Embedded vs standalone modes
3. **Page Context Stripping**: SDK removes asset context in embedded mode
4. **Python Version**: Must use 3.11.10 (not newer)

---

**Last Updated**: March 2026