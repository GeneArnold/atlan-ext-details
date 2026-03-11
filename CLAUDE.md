# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a local test harness for developing web applications that integrate with Atlan's platform via iframe embedding. The project simulates Atlan's postMessage protocol, allowing developers to build and test custom apps without requiring a live Atlan instance.

## Commands

### Running the Project
```bash
# Option 1: Using npx serve
npx serve

# Option 2: Using Python's built-in server
python -m http.server 8000

# Then open http://localhost:8000 in your browser
```

Since this is a vanilla HTML/JavaScript project with no build tools, simply serve the files with any HTTP server and open index.html.

## Architecture & Key Concepts

### Project Structure
The project implements a mock Atlan parent page (`index.html`) that hosts an embedded customer app (`embedded-app.html`) in an iframe, communicating via postMessage protocol.

### postMessage Protocol Sequence
The critical handshake between Atlan (parent) and the embedded app:

1. **Atlan → App**: `ATLAN_HANDSHAKE` with `{ appId }`
2. **App → Atlan**: `IFRAME_READY` (must respond within 10 seconds)
3. **Atlan → App**: `ATLAN_AUTH_CONTEXT` with auth token, user info, and page context
4. **App → Atlan**: `IFRAME_TOKEN_REQUEST` (when token needs refresh)
5. **Atlan → App**: `ATLAN_LOGOUT` (on session end)

### Security Requirements
- **All postMessage calls must use explicit targetOrigin** (never `'*'`)
- **Both sides must validate message origin** before processing
- Tokens should be stored in memory only (not localStorage/cookies)
- Request token refresh 5 minutes before expiry

### Deployment Modes
The app can be deployed in two modes once integrated with real Atlan:

- **Direct Mode**: Hosted on Atlan's infrastructure, automatic SSO
- **SDR Mode**: Self-hosted, requires OAuth 2.0 with PKCE

### Integration Points
Apps can appear in:
- `nav-tab`: Left navigation panel
- `asset-profile-tab`: Tab on asset detail pages (receives asset GUID)
- Complete redirect: Opens in new window
- Preview modal: Modal iframe overlay

## Key Implementation Files

- **`index.html`**: Mock Atlan parent page that loads the iframe and manages the postMessage protocol from Atlan's side
- **`embedded-app.html`**: Customer app that handles the protocol from the embedded app's side
- **`atlan-sot.md`**: Complete specification document for Atlan's iframe integration architecture
- **`claude-code-prompt.md`**: Detailed scaffolding instructions for building the test harness

## Important Specifications

### Auth Context Payload Structure
```javascript
{
  type: "ATLAN_AUTH_CONTEXT",
  payload: {
    token: "JWT_TOKEN",
    expiresAt: 1234567890,  // Unix seconds
    user: { id, username, email, name },
    page: { route, params: { id: "asset-guid" }, query },
    timestamp: 1234567890000  // Unix ms
  }
}
```

### iframe Sandbox Permissions
```html
sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
```
Note: No `allow-top-navigation` - apps cannot redirect the parent window.

## Development Notes

- This is a **vanilla HTML/JavaScript project** - no npm, webpack, or build tools required
- The project currently consists of specification documents - the HTML implementation needs to be created
- When implementing, ensure strict origin validation for all postMessage communications
- The mock parent should log all messages for debugging
- The embedded app should display connection status and handle token expiry proactively