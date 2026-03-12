# Atlan Auth SDK Integration Issues

## Overview
During implementation of the External Details Tab, we discovered several inconsistencies in the Atlan Auth SDK that should be addressed.

## Issue 1: Inconsistent User Data Structure

The SDK returns completely different user data structures depending on the mode:

### Standalone Mode (Direct Access)
```json
{
  "userId": "072c2b06-9501-4c5b-b641-faae4e7ca3b0",
  "username": "gene.arnold@atlan.com",
  "workspaceRole": "$admin",
  "assignedRole": {
    "id": "111325b6-c10c-4068-a58c-473cecf0229c",
    "name": "$admin",
    "description": "Admin"
  },
  "profileRole": "Machine Learning Engineer",
  "designation": "",
  "groups": [],
  "permissions": [...200+ permissions],
  "roles": [...200+ roles]
}
```

### Embedded Mode (Inside Atlan iframe)
```json
{
  "id": "072c2b06-9501-4c5b-b641-faae4e7ca3b0",
  "username": "gene.arnold@atlan.com",
  "email": "gene.arnold@atlan.com",
  "name": "Gene Arnold"
}
```

### Key Differences:
- **User ID field**: `userId` vs `id`
- **Email**: Combined in `username` (standalone) vs separate `email` field (embedded)
- **Display name**: Not provided (standalone) vs `name` field (embedded)
- **Permissions/Roles**: Full context (standalone) vs not provided (embedded)

## Issue 2: Missing Asset Context in Embedded Mode

When running as an external tab on an asset page:

### Expected Behavior
The SDK should provide the current asset's GUID through `authContext.page.params.id`

### Actual Behavior
- No `page` object in `authContext` at all
- Asset GUID is not passed via iframe URL parameters
- Asset GUID is not sent via postMessage

### authContext Structure
```javascript
// Embedded mode authContext only contains:
{
  token: "JWT_TOKEN",
  user: {...},  // Simple user object
  tenant: "tenant-info",
  mode: "embedded"
  // Missing: page context with asset information
}
```

## Impact on Development

1. **Extra Complexity**: Developers must handle two completely different data structures
2. **Missing Features**: Cannot access asset context in embedded mode
3. **Inconsistent Experience**: Different information available in different modes

## Workaround Code

```javascript
// Handle different user ID fields
const userId = user?.userId || user?.id || 'N/A';

// Handle different email fields
const email = user?.email || user?.username || 'N/A';

// Asset GUID - currently no solution for embedded mode
const assetGuid = authContext.page?.params?.id || null;
```

## Recommendations for Atlan

1. **Standardize User Object**: Use consistent field names across modes
2. **Include Asset Context**: Pass asset GUID to embedded apps via:
   - URL parameter (e.g., `?assetId=GUID`)
   - postMessage after authentication
   - Include `page` context in embedded mode authContext
3. **Document Differences**: If differences must exist, clearly document them

## Test URLs

- **Standalone**: https://atlan-ext-details.onrender.com
- **Embedded**: View in Atlan at https://fs3.atlan.com on any Table/Column asset

## Related Files

- `templates/index.html`: Contains workarounds for field differences
- `app.py`: Backend expecting asset GUID for API calls

---

**Note**: This documentation created March 2026 during External Tab implementation.
Contact: Gene Arnold (gene.arnold@atlan.com)