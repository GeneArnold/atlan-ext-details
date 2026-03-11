# Atlan Custom Tab Integration - Complete Reference Package

## 🎯 Purpose

This directory contains everything needed to build a custom tab integration for Atlan. It includes working examples, critical documentation, and battle-tested implementations that solve common problems like race conditions.

## 📁 What's Included

### Core Documentation
- **`atlan-sot.md`** - Complete Atlan iframe integration specification
- **`claude-code-prompt.md`** - Detailed implementation instructions
- **`CLAUDE.md`** - Project overview and architecture guidance
- **`RACE_CONDITION_ANALYSIS.md`** - Critical timing issues and solutions

### Working Examples
- **`simple-tab-template.html`** - Complete working example of a simple tab
- **`postmessage-implementation.js`** - Battle-tested PostMessage code with race condition fixes
- **`oauth-example/`** - Full OAuth 2.0 implementation with PKCE

### Deployment Files
- **`requirements-example.txt`** - Python dependencies for Flask apps
- **`Procfile-example`** - Render deployment configuration
- **`.python-version-example`** - Python version specification (3.11.10)

### Credentials (Development Only)
- **`oauth-credentials.md`** - OAuth client details for testing

## 🚀 Quick Start

### Option 1: Simple HTML Tab

1. Start with `simple-tab-template.html`
2. Modify the `loadAsset()` function to call your backend
3. Test locally with `?test=true` parameter
4. Deploy to your hosting service

### Option 2: Flask Backend with Frontend

```python
# app.py
from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('tab.html')

@app.route('/api/asset/<guid>')
def get_asset(guid):
    # Your logic here
    return jsonify({'success': True, 'data': {}})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Option 3: OAuth-Enabled App

See the complete `oauth-example/` directory for a Docker-based OAuth implementation.

## 🔑 Critical Implementation Points

### 1. PostMessage Race Condition Prevention

**THE MOST IMPORTANT THING:** Set up message listeners IMMEDIATELY!

```javascript
// WRONG - Will cause race conditions
window.addEventListener('load', () => {
    window.addEventListener('message', handler);
});

// CORRECT - Set up immediately
window.addEventListener('message', handler);
```

### 2. State Management

```javascript
// Use undefined for "not checked yet"
let isConfigured = undefined;  // NOT false!

// Check state properly
if (isConfigured === undefined) {
    await checkConfiguration();
}
```

### 3. Security

```javascript
// ALWAYS validate origin
const allowedOrigins = [
    'https://home.atlan.com',
    'https://partner-sandbox.atlan.com'
];

// NEVER use '*' for postMessage
window.parent.postMessage(data, event.origin);  // Good
window.parent.postMessage(data, '*');           // Bad!
```

### 4. Proactive Fallback

```javascript
// Send IFRAME_READY after 500ms if no handshake
setTimeout(() => {
    if (!handshakeReceived) {
        window.parent.postMessage({
            type: 'IFRAME_READY',
            payload: { ready: true }
        }, parentOrigin);
    }
}, 500);
```

## 📋 PostMessage Protocol

The complete flow between Atlan and your iframe:

1. **Atlan → iframe**: `ATLAN_HANDSHAKE`
2. **iframe → Atlan**: `IFRAME_READY`
3. **Atlan → iframe**: `ATLAN_AUTH_CONTEXT` (with asset GUID)
4. **iframe**: Load and display content
5. **iframe → Atlan**: `IFRAME_TOKEN_REQUEST` (if token expires)
6. **Atlan → iframe**: `ATLAN_LOGOUT` (on session end)

## 🛠 Development Tips

### Local Testing

Add these query parameters for testing:
- `?test=true` - Simulates Atlan messages
- `?debug=true` - Shows debug panel

### Debugging

Use prefixed console logs:
```javascript
console.log('[INIT] Starting initialization');
console.log('[MESSAGE] Received:', data);
console.log('[HANDSHAKE] Processing handshake');
console.log('[AUTH_CONTEXT] Loading asset:', guid);
```

### Browser Testing

1. Always test in incognito mode
2. Clear cache between tests
3. Check browser console for errors
4. Monitor network tab for failed requests

## 🚢 Deployment

### For Render

1. Create `.python-version` with `3.11.10`
2. Add `Procfile` with: `web: gunicorn app:app`
3. Set environment variables in Render dashboard
4. Enable auto-deploy from GitHub

### For Static HTML

1. Any static hosting works (GitHub Pages, Netlify, Vercel)
2. Ensure HTTPS is enabled
3. Configure CORS if needed

## 🐛 Common Issues and Solutions

### Issue: "Chat errors on initial load but works after refresh"
**Solution**: Message listener not set up early enough. See `RACE_CONDITION_ANALYSIS.md`

### Issue: "Python version incompatibility"
**Solution**: Use Python 3.11.10 specifically (see `.python-version-example`)

### Issue: "No handshake received"
**Solution**: Check allowed origins list and ensure iframe sandbox permissions

### Issue: "Asset GUID is undefined"
**Solution**: Validate payload structure defensively:
```javascript
if (payload?.page?.params?.id) {
    // Safe to use payload.page.params.id
}
```

## 📚 Essential Reading Order

1. Start with `simple-tab-template.html` - See a working example
2. Read `postmessage-implementation.js` - Understand the critical parts
3. Review `RACE_CONDITION_ANALYSIS.md` - Learn from our mistakes
4. Study `atlan-sot.md` - Understand the full protocol
5. Check `oauth-example/` if you need authentication

## 🎓 Key Lessons Learned

1. **Timing is everything** - Set up listeners before anything else
2. **State matters** - Use `undefined` for uninitialized states
3. **Be defensive** - Always validate data and add retry logic
4. **Log everything** - Use prefixed logs for debugging
5. **Test the unhappy path** - Clear cache, use incognito, test errors

## 💡 Tips for New Implementation

When building your tab:

1. **Start simple** - Get the handshake working first
2. **Add incrementally** - Don't try to build everything at once
3. **Test often** - Use the test mode parameters
4. **Log verbosely** - You can remove logs later
5. **Handle errors** - Users will do unexpected things

## 🔗 Integration with Atlan

Your tab configuration in Atlan should point to:
- **URL**: Your deployed application URL
- **Type**: `asset-profile-tab` (for asset detail pages)
- **Permissions**: Appropriate sandbox permissions

## 📞 Getting Help

1. Check the debug console first
2. Review `RACE_CONDITION_ANALYSIS.md` for timing issues
3. Look at working examples in this directory
4. Test with `?debug=true` to see message flow

## ✅ Checklist for New Tab

- [ ] Message listener set up immediately
- [ ] Origin validation implemented
- [ ] IFRAME_READY response working
- [ ] AUTH_CONTEXT handler extracts asset GUID
- [ ] Error states handled gracefully
- [ ] Retry logic for network requests
- [ ] Logging with prefixes
- [ ] Test mode for local development
- [ ] Proactive IFRAME_READY fallback
- [ ] Security: No '*' in postMessage

---

**Remember**: The race condition fix is all about TIMING. Set up your listeners early, check your state properly, and always have a fallback plan!

Good luck with your implementation! 🚀