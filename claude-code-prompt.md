# Claude Code Prompt — Atlan Embedded App Test Harness

Paste this entire prompt into a Claude Code session to scaffold the project.

---

## PROMPT START

I'm building a local test harness to prototype and develop a custom web app that will eventually be embedded inside Atlan's UI via their iframe integration framework. I need two things built in the same project: a mock Atlan parent page that simulates the postMessage protocol, and a sample embedded app that responds to it. This lets me develop the integration locally without needing a live Atlan instance.

---

### Background: How Atlan's iframe integration works

Atlan embeds customer apps in a sandboxed iframe and uses a postMessage-based handshake to pass auth context. Here is the full protocol:

**Handshake sequence:**
1. Atlan loads the customer app URL in an iframe
2. Atlan sends `ATLAN_HANDSHAKE` with `{ appId: string }`
3. The app must respond with `IFRAME_READY` within 10 seconds
4. Atlan sends `ATLAN_AUTH_CONTEXT` with the full auth payload
5. The app can request a fresh token anytime via `IFRAME_TOKEN_REQUEST`
6. Atlan resends `ATLAN_AUTH_CONTEXT` every 15 minutes automatically
7. Atlan sends `ATLAN_LOGOUT` when the session ends

**Messages Atlan → App:**
- `ATLAN_HANDSHAKE` → `{ appId: string }`
- `ATLAN_AUTH_CONTEXT` → full auth payload (see below)
- `ATLAN_LOGOUT` → no payload

**Messages App → Atlan:**
- `IFRAME_READY` → no payload (required, must fire within 10s)
- `IFRAME_TOKEN_REQUEST` → no payload
- `IFRAME_ERROR` → `{ message: string }`

**Auth context payload shape:**
```json
{
  "type": "ATLAN_AUTH_CONTEXT",
  "payload": {
    "token": "mock-jwt-token-xyz",
    "expiresAt": 1999999999,
    "user": {
      "id": "user-123",
      "username": "gene.doe",
      "email": "gene@company.com",
      "name": "Gene Doe"
    },
    "page": {
      "route": "/assets/abc-123",
      "params": { "id": "asset-guid-abc-123" },
      "query": {}
    },
    "timestamp": 1700000000000
  }
}
```

**Security rules:**
- postMessage must always use explicit `targetOrigin`, never `'*'`
- Both sides must validate the origin of every incoming message
- Tokens stored in memory only, never localStorage

---

### What to build

**Project structure:**
```
atlan-iframe-harness/
├── index.html         # Mock Atlan parent
├── embedded-app.html  # The customer app (loaded in the iframe)
└── README.md
```

No build tools, no npm, no bundlers. Pure HTML + vanilla JavaScript only. It needs to run by just opening `index.html` in a browser or serving with `npx serve` or `python -m http.server`.

---

**File 1: `index.html` — Mock Atlan Parent**

This simulates what the real Atlan UI does. It should:

- Have a clean UI styled to loosely resemble Atlan (dark sidebar on the left, main content area on the right)
- Load `embedded-app.html` in an iframe in the main content area
- Automatically send `ATLAN_HANDSHAKE` after the iframe loads
- Listen for `IFRAME_READY` and then send `ATLAN_AUTH_CONTEXT` with mock data
- Have a visible **event log panel** that shows every message sent and received with timestamps
- Have control buttons:
  - **Send Auth Context** — manually resend `ATLAN_AUTH_CONTEXT`
  - **Send Token Refresh** — resend auth context simulating a token refresh (update the token value and expiresAt)
  - **Send Logout** — send `ATLAN_LOGOUT`
  - **Simulate Asset Change** — resend auth context with a different asset GUID and route to simulate navigating to a different asset
- Have an editable JSON field showing the current mock auth payload so I can modify it and resend
- Use explicit targetOrigin set to `window.location.origin` for all postMessage calls
- Validate the origin of all incoming messages

---

**File 2: `embedded-app.html` — The Customer App**

This is the app that will eventually be hosted and registered with Atlan. It should:

- Handle the full postMessage handshake protocol correctly
- Display a clean UI showing:
  - Connection status (Waiting for handshake → Connected → Authenticated)
  - The logged-in user's name and email
  - The current asset GUID from `page.params.id`
  - Token expiry countdown (live, updates every second)
  - The full raw auth context as formatted JSON (collapsible)
- Have a **Request Token Refresh** button that sends `IFRAME_TOKEN_REQUEST`
- Have a **Report Error** button that sends `IFRAME_ERROR` with a sample message
- Have a **Simulate API Call** button that shows what a real Atlan API call would look like using the token (mock the fetch, don't actually call anything — just log the request details it would make to `/api/meta/entity/guid/{asset-id}`)
- Proactively check token expiry every 60 seconds and auto-request refresh if less than 5 minutes remain
- Handle `ATLAN_LOGOUT` gracefully (clear state, show logged-out UI)
- Use explicit targetOrigin set to `window.location.origin` for all postMessage calls
- Validate the origin of all incoming messages

---

**File 3: `README.md`**

Include:
- How to run it locally (both `npx serve` and `python -m http.server` options)
- A summary of the protocol
- What to change when connecting to a real Atlan instance (origin URL, real token handling)
- Notes on what Direct Mode vs SDR Mode means for auth when going to production

---

### Additional requirements

- The two pages must work correctly when served from the same local origin (e.g., `http://localhost:3000`)
- Use clear comments in the code explaining each step of the protocol
- Make the UI look polished enough to demo to stakeholders — this may become a reference implementation
- Use only browser-native APIs, no external dependencies

---

### After scaffolding

Once the files are created, please:
1. Start a local server and confirm both pages load without errors
2. Walk me through how to verify the handshake is working correctly in the browser console
3. Tell me what the most likely failure modes are and how to debug them

## PROMPT END
