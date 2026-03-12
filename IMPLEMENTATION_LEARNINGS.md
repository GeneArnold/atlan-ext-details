# Atlan External Tab Implementation Learnings

## Overview
This document captures critical learnings from implementing an external tab integration with Atlan using the `@atlanhq/atlan-auth` SDK. These findings are essential for future developers working with Atlan's iframe integration.

## Table of Contents
1. [Authentication Flow](#authentication-flow)
2. [Critical Issue: Asset GUID Capture](#critical-issue-asset-guid-capture)
3. [Data Structure Inconsistencies](#data-structure-inconsistencies)
4. [Backend Integration Challenges](#backend-integration-challenges)
5. [Working Solutions](#working-solutions)
6. [Recommendations](#recommendations)

---

## Authentication Flow

### How It Works
1. **SDK Loading**: Load Atlan Auth SDK from CDN
   ```html
   <script src="https://unpkg.com/@atlanhq/atlan-auth@latest/dist/atlan-auth.umd.min.js"></script>
   ```

2. **SDK Initialization**:
   ```javascript
   const atlan = new AtlanAuth({
       origin: 'https://fs3.atlan.com',
       onReady: (context) => { /* handle auth */ },
       onError: (error) => { /* handle error */ }
   });
   atlan.init();
   ```

3. **Two Authentication Modes**:
   - **Embedded Mode**: Running inside Atlan iframe
   - **Standalone Mode**: Direct browser access for testing

### Key Finding
The SDK simplifies OAuth from 200+ lines to ~10 lines, handling both embedded and standalone modes automatically.

---

## Critical Issue: Asset GUID Capture

### The Problem
When running as an external tab on an asset page, the app needs the current asset's GUID to fetch and display relevant information.

### Discovery Process
1. **Initial Assumption**: Asset GUID would be in `authContext.page.params.id`
2. **Reality in Embedded Mode**: SDK strips the page context entirely
3. **Investigation**: Checked URL params, hash, authContext properties - all empty
4. **Breakthrough**: Found working examples using raw postMessage handlers

### Root Cause
The Atlan Auth SDK **strips the page context** from the `ATLAN_AUTH_CONTEXT` message when processing it in embedded mode.

### The Solution
Capture the asset GUID from the raw postMessage BEFORE the SDK processes it:

```javascript
let assetGuidFromMessage = null;

// Add this BEFORE initializing the SDK
window.addEventListener('message', (event) => {
    if (event.origin !== ATLAN_INSTANCE_URL) return;

    const { type, payload } = event.data || {};

    if (type === 'ATLAN_AUTH_CONTEXT') {
        // The raw message DOES contain the asset GUID!
        if (payload?.page?.params?.id) {
            assetGuidFromMessage = payload.page.params.id;
            console.log('Asset GUID captured:', assetGuidFromMessage);
        }
    }
});

// Then in your display logic:
const assetGuid = mode === 'embedded' ? assetGuidFromMessage : authContext.page?.params?.id;
```

### Timeline
- **Initial Implementation**: No asset GUID available
- **Debugging Phase**: Added extensive logging, checked all possible sources
- **Solution Found**: Examined working examples (`simple-tab-template.html`)
- **Fix Applied**: Raw postMessage listener before SDK init

---

## Data Structure Inconsistencies

### User Object Differences

#### Standalone Mode (Full Context)
```json
{
  "userId": "072c2b06-9501-4c5b-b641-faae4e7ca3b0",
  "username": "gene.arnold@atlan.com",
  "workspaceRole": "$admin",
  "profileRole": "Machine Learning Engineer",
  "permissions": [...200+ permissions],
  "roles": [...200+ roles]
}
```

#### Embedded Mode (Basic Profile)
```json
{
  "id": "072c2b06-9501-4c5b-b641-faae4e7ca3b0",
  "username": "gene.arnold@atlan.com",
  "email": "gene.arnold@atlan.com",
  "name": "Gene Arnold"
}
```

### Key Differences
| Field | Standalone | Embedded |
|-------|------------|----------|
| User ID | `userId` | `id` |
| Email | In `username` | Separate `email` field |
| Display Name | Not provided | `name` field |
| Permissions | Full array | Not provided |
| Roles | Full array | Not provided |

### Handling Both Modes
```javascript
// Adaptive field handling
const userId = user?.userId || user?.id;
const email = user?.email || user?.username;
const displayName = user?.name || 'N/A';

// Only show fields that exist
${user?.workspaceRole ? `<div>Role: ${user.workspaceRole}</div>` : ''}
```

---

## Backend Integration Solution

### The Problem
The OAuth JWT token from authentication cannot be used as an API key for the pyatlan SDK.

### The Solution
Use Atlan's REST API directly with the Bearer token:

```python
@app.route('/api/asset/<guid>')
def get_asset(guid):
    # Extract Bearer token from header
    token = auth_header.replace('Bearer ', '')

    # Use Atlan REST API directly
    api_url = f"{ATLAN_BASE_URL}/api/meta/entity/guid/{guid}"

    headers = {
        'Authorization': f'Bearer {token}',  # OAuth token as Bearer
        'Content-Type': 'application/json'
    }

    response = requests.get(api_url, headers=headers)
    asset_data = response.json()

    # Parse the Atlan API response structure
    entity = asset_data.get('entity', asset_data)
    attributes = entity.get('attributes', {})
```

### Key Differences
| Approach | Authentication | Result |
|----------|---------------|---------|
| pyatlan SDK | API Key expected | ❌ 500 Error |
| REST API | Bearer token | ✅ Works |

### Current Status
- ✅ Authentication token passed as Bearer
- ✅ Asset GUID captured from postMessage
- ✅ Asset details fetched successfully
- ✅ Data displayed in UI

---

## Working Solutions

### 1. Asset GUID Capture
✅ **SOLVED**: Use raw postMessage listener before SDK initialization

### 2. User Information Display
✅ **SOLVED**: Adaptive field checking for both modes

### 3. Authentication
✅ **SOLVED**: SDK handles both modes automatically

### 4. Asset Data Fetching
✅ **SOLVED**: Use Atlan REST API with OAuth Bearer token

---

## Recommendations

### For Atlan Team

1. **SDK Enhancement**: Don't strip page context in embedded mode
   ```javascript
   // Should preserve:
   authContext.page = {
       params: { id: 'asset-guid' },
       route: '/assets/...',
       query: {}
   }
   ```

2. **Documentation**: Document the data structure differences between modes

3. **Token Usage**: Clarify if OAuth tokens can be used with pyatlan SDK

4. **Consistent User Object**: Standardize field names across modes

### For Developers

1. **Always Use Raw Listeners**: Capture critical data before SDK processing
2. **Handle Both Modes**: Check for different field names
3. **Extensive Logging**: Add console.log for all postMessages
4. **Test Both Modes**: Standalone and embedded behave differently

---

## File Structure Reference

```
/atlan-ext-details/
├── app.py                    # Flask backend (pyatlan integration)
├── templates/
│   └── index.html           # Main app with workarounds
├── ATLAN_SDK_ISSUES.md     # Detailed SDK issues
├── IMPLEMENTATION_LEARNINGS.md  # This file
├── simple-tab-template.html # Working reference example
└── complex-example-chat.html # Advanced reference example
```

---

## Critical Code Patterns

### Pattern 1: Dual-Mode Authentication
```javascript
const atlan = new AtlanAuth({
    origin: ATLAN_INSTANCE_URL,
    onReady: (context) => {
        const mode = context.mode; // 'embedded' or 'standalone'
        // Handle differently based on mode
    }
});
```

### Pattern 2: Asset Context Capture
```javascript
// Must be BEFORE SDK init
window.addEventListener('message', (event) => {
    if (type === 'ATLAN_AUTH_CONTEXT') {
        assetGuid = payload?.page?.params?.id;
    }
});
```

### Pattern 3: Adaptive Field Display
```javascript
// Only show what exists
${field ? `<div>${field}</div>` : ''}
```

---

## Debugging Checklist

When things don't work:

1. ✅ Check browser console for all messages
2. ✅ Verify Atlan instance URL matches exactly
3. ✅ Confirm redirect URIs are registered
4. ✅ Add raw postMessage listener for debugging
5. ✅ Log authContext structure in both modes
6. ✅ Check network tab for API calls
7. ✅ Verify token is being passed in headers
8. ✅ Test in both standalone and embedded modes

---

## Next Steps

1. **Resolve Backend 500 Error**:
   - Investigate if OAuth token can be used with pyatlan
   - Consider using service account or API token instead
   - Check Atlan documentation for proper auth flow

2. **Complete Testing**:
   - Verify asset details display when backend is fixed
   - Test with different asset types
   - Validate in production Atlan instance

3. **Documentation**:
   - Update README with learnings
   - Create troubleshooting guide
   - Document the complete auth flow

---

**Last Updated**: March 2026
**Author**: Gene Arnold
**Status**: Asset GUID ✅ | User Info ✅ | Backend Integration ✅

## Complete Working Solution

The External Details Tab is now fully functional with all three critical components working:

1. **Asset GUID Capture**: Using raw postMessage listener before SDK initialization
2. **User Information**: Adaptive display for both standalone and embedded modes
3. **Backend Integration**: Direct REST API calls with OAuth Bearer token

The app successfully displays asset information when running as an external tab in Atlan!