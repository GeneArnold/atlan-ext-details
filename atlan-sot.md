# Atlan Custom Frontend Apps — Single Source of Truth

## What Is This?

Atlan supports embedding custom web applications directly inside the Atlan UI. Customers build their own web apps (any JS framework or plain HTML) and have them appear natively within Atlan at predefined integration points. The apps run on the customer's own infrastructure (or optionally inside Atlan's cluster) and communicate with Atlan through a sandboxed iframe + postMessage protocol.

---

## Deployment Modes

### A. Direct Mode (Hosted on Atlan)
- App is deployed into the customer's Atlan instance cluster
- App is served by a **FastAPI backend** bundled with Atlan's App Framework (handles serving the frontend bundle, auth flows, and token handling — you don't write this yourself)
- SSO is automatic — the app inherits Atlan's session and networking context, no separate login needed
- CORS is not a concern since everything is within the same domain

### B. SDR Mode (Self-Deployed Runtime — Hosted on Customer Infra)
- App runs on customer-owned infrastructure, outside Atlan's domain
- Must be web-accessible for Atlan to load it in an iframe
- Requires its own auth flow: **OAuth 2.0 Authorization Code Flow with PKCE**
  - User is redirected to Atlan's IdP (Keycloak)
  - Keycloak delegates to the customer's upstream IdP
  - Authorization code is exchanged for an access token
  - App stores session token for subsequent API calls
- CORS is relevant here since you're crossing domain boundaries
- Ideal for customers with strict data-residency or IT controls

---

## Integration Points (Where Apps Can Appear)

### 1. Left Navigation Panel (`nav-tab`)
- Adds an entry to Atlan's left nav
- Clicking navigates to `/external/{app-id}` where the app loads full-screen
- No tight coupling to asset context required
- Best for large, self-contained experiences (e.g., a custom Data Products module)

### 2. Asset Profile Tab (`asset-profile-tab`)
- Adds a new tab on asset detail pages
- App is rendered in an iframe within the profile section
- Receives the asset GUID via `page.params.id` in the auth context
- Supports conditional rendering by asset type (e.g., only show on Table, View, Column)
- Optional CTA in the Overview sidebar can redirect users to this tab
- Works across: Assets, Data Products, Glossary, AI assets

### 3. Complete Redirect
- A custom CTA button appears in the Asset Profile action bar
- Clicking opens the external app in a new browser window
- Mirrors the existing "View in [source]" pattern (e.g., "View in Tableau")
- No iframe/postMessage required — just a URL launch with context passed as params

### 4. Preview (Modal Embed)
- A custom CTA opens the app inside a modal iframe overlay
- Mirrors Atlan's existing "Preview" experience for BI dashboards
- Best for lightweight, read-only inspections tied to the current asset

> **Note:** An app can be configured in multiple slots simultaneously.

---

## The postMessage Handshake Protocol

This is the communication contract between Atlan (parent) and your app (iframe). Only applies to iframe-based integration points (nav-tab, asset-profile-tab, modal embed).

### Sequence

```
Atlan Parent                          Customer App (iframe)
     |                                        |
     |  1. Load iframe (src=app URL)          |
     | -------------------------------------> |
     |                                        |
     |  2. ATLAN_HANDSHAKE { appId }          |
     | -------------------------------------> |
     |                                        |
     |  3. IFRAME_READY                       |
     | <------------------------------------- |
     |    (must happen within 10 seconds)     |
     |                                        |
     |  4. ATLAN_AUTH_CONTEXT                 |
     |     { token, user, page, expiresAt }   |
     | -------------------------------------> |
     |                                        |
     |  5. IFRAME_TOKEN_REQUEST (on demand)   |
     | <------------------------------------- |
     |                                        |
     |  6. ATLAN_AUTH_CONTEXT (refreshed)     |
     | -------------------------------------> |
     |                                        |
     |  7. ATLAN_LOGOUT (on session end)      |
     | -------------------------------------> |
```

### Messages: Atlan → App

| Message | Payload | When |
|---|---|---|
| `ATLAN_HANDSHAKE` | `{ appId: string }` | Immediately after iframe loads |
| `ATLAN_AUTH_CONTEXT` | See below | After IFRAME_READY, on token refresh, on demand |
| `ATLAN_LOGOUT` | none | When user logs out or session ends |

### Messages: App → Atlan

| Message | Payload | When |
|---|---|---|
| `IFRAME_READY` | none | Required. After app initializes. Must fire within 10s |
| `IFRAME_TOKEN_REQUEST` | none | When app needs a fresh token before current one expires |
| `IFRAME_ERROR` | `{ message: string }` | To surface an error in the Atlan UI |

### Auth Context Payload (ATLAN_AUTH_CONTEXT)

```json
{
  "type": "ATLAN_AUTH_CONTEXT",
  "payload": {
    "token": "string",          // JWT for Atlan API calls
    "expiresAt": 1234567890,    // Unix seconds
    "user": {
      "id": "string",
      "username": "string",
      "email": "string",
      "name": "string"
    },
    "page": {
      "route": "/assets/abc-123",
      "params": { "id": "asset-guid-here" },  // id = asset GUID when on asset profile
      "query": {}
    },
    "timestamp": 1234567890000  // Unix ms
  }
}
```

### Security Rules for postMessage
- All communication uses explicit `targetOrigin` — **never `'*'`**
- Both sides must validate the origin of every incoming message
- Rate limited to 10 messages/second per iframe
- App cannot access Atlan's DOM, cookies, or localStorage
- App cannot navigate the parent window (no `allow-top-navigation`)

### Token Best Practices
- Store tokens in memory only — not localStorage or cookies
- Monitor `expiresAt` and send `IFRAME_TOKEN_REQUEST` at least 5 minutes before expiry
- Atlan automatically resends `ATLAN_AUTH_CONTEXT` with a refreshed token every 15 minutes
- Clear all tokens immediately on `ATLAN_LOGOUT`

---

## What the App Knows About the Current Asset

From the handshake alone, the app receives:
- The asset's **GUID** (`page.params.id`)
- The current **route**
- Route **params** and **query strings**

To get full asset details (name, type, owners, tags, lineage, schema, etc.), use the GUID + JWT to call the Atlan API:

```
GET https://{atlan-instance}/api/meta/entity/guid/{asset-guid}
Authorization: Bearer {token}
```

The JWT carries the logged-in user's existing permissions — no privilege escalation is possible. The app can read and write anything that user is allowed to do.

---

## App Configuration (How Atlan Registers Your App)

Currently managed via a **LaunchDarkly feature flag** (`external-iframe-tabs`) pushed per tenant by the Atlan team. No code deployment needed on Atlan's side. Self-serve configuration is on the roadmap but not available in Phase 1.

### Config Format

```json
{
  "your-app-id": {
    "display_name": "Your App Name",
    "iframe_url": "https://your-app.example.com",
    "allowed_origins": ["https://your-app.example.com"],
    "icon": "Analytics",
    "description": "What this app does",
    "render_at": [
      {
        "slot": "asset-profile-tab",
        "when": {
          "assetTypes": ["Table", "View", "MaterialisedView", "Column"]
        }
      },
      {
        "slot": "nav-tab"
      }
    ]
  }
}
```

### Config Fields

| Field | Required | Description |
|---|---|---|
| `display_name` | Yes | Label shown in the UI |
| `iframe_url` | Yes | Your app's URL (must be http/https) |
| `allowed_origins` | Yes | Origins for postMessage scoping. Supports wildcards: `https://*.example.com` |
| `icon` | No | Icon from Atlan icon set (default: Analytics) |
| `description` | No | Shown in navigation |
| `render_at` | Yes | Array of `{ slot, when? }` objects |

### Asset Type Names (Case-Sensitive)
`Table`, `View`, `MaterialisedView`, `Column`, `AtlasGlossary`, `AtlasGlossaryTerm`, `AtlasGlossaryCategory`, `Connection`, `Database`, `Schema`

### Route-Based Conditions (Alternative to assetTypes)
```json
{ "when": { "routes": ["/assets/*", "/glossary/**"] } }
```

---

## Iframe Sandbox Permissions

```
allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox
```

Notably absent: `allow-top-navigation` — the embedded app cannot redirect the parent window.

---

## Release Timeline

| Phase | Features | Target |
|---|---|---|
| Phase 1 — Integration | Embedding layer (nav, tabs, modal, redirect), config-driven iframe provisioning, SSO for Direct Mode, OAuth PKCE for SDR Mode | March 2026 |
| Phase 2 — Framework Tooling | Boilerplate starter templates, UI utility libraries, shared design tokens, pre-built integration helpers | June 2026 |

---

## Testing Without a Live Atlan Instance

You can fully develop and test your app's integration logic without Atlan involvement by building a mock parent page that simulates the postMessage sequence:

1. Build a simple HTML page that loads your app in an iframe
2. Have it send `ATLAN_HANDSHAKE` after load
3. Listen for `IFRAME_READY`, then send `ATLAN_AUTH_CONTEXT` with mock data
4. Add buttons to simulate token refresh and logout

Once validated locally, Atlan configures the LaunchDarkly flag on a staging tenant for end-to-end testing.

---

## How to Engage Atlan to Enable This

1. Decide your deployment mode (Direct vs SDR)
2. Build and host your app (or test locally first)
3. Ask Atlan to push the config via the `external-iframe-tabs` LaunchDarkly flag for your tenant
4. Validate on a staging/dev tenant before production
