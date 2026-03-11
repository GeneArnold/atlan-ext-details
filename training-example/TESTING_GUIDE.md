# 🧪 Testing Guide for Atlan External Tab Training Example

## Quick Test (2 minutes)

### 1. Check Setup
```bash
python test_setup.py
```
✅ All dependencies should show as installed

### 2. Test Backend Health Check
```bash
# Start the backend
python backend.py

# In another terminal, test health endpoint
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Atlan training backend is running"
}
```

## Full Integration Test (10 minutes)

### Test 1: Standalone Mode (Local Development)

This tests OAuth authentication without needing Atlan.

1. **Update the Atlan URL** in `index.html` (line ~157):
   ```javascript
   origin: 'https://your-actual-tenant.atlan.com',
   ```

2. **Start the backend**:
   ```bash
   python backend.py
   ```

3. **Start the frontend** (new terminal):
   ```bash
   python -m http.server 8000
   ```

4. **Open in browser**: http://localhost:8000

5. **What should happen**:
   - Browser redirects to Atlan login page
   - After login, redirects back to your app
   - You see:
     - ✅ Authentication Status: "Authenticated"
     - ✅ Mode: "standalone"
     - ✅ Your user information
     - ⚠️ Asset GUID: "Not available (standalone mode)" - This is expected!

### Test 2: Embedded Mode (Inside Atlan)

This tests the full integration with asset data.

1. **Configure in Atlan**:
   - Add your app as an external tab in Atlan
   - URL: `http://localhost:8000` (or wherever you're hosting)

2. **Navigate to an asset** in Atlan (table, column, glossary term, etc.)

3. **Click your external tab**

4. **What should happen**:
   - ✅ No login redirect (already authenticated)
   - ✅ Mode: "embedded"
   - ✅ Your user information displays
   - ✅ Asset GUID shows (e.g., "abc-123-def-456")
   - ✅ Asset description loads from backend

## Component Testing

### Test Backend Independently

You can test the backend without the frontend using the test endpoint:

```bash
# Get a valid token from Atlan (you can get this from browser DevTools)
TOKEN="your-jwt-token-here"
GUID="some-asset-guid"

# Test the endpoint
curl -X POST http://localhost:5000/api/test-asset \
  -H "Content-Type: application/json" \
  -d "{\"guid\": \"$GUID\", \"token\": \"$TOKEN\"}"
```

### Test Frontend Authentication Only

1. Open `index.html` in browser
2. Open Browser DevTools Console (F12)
3. Look for logs starting with `[TRAINING]`:
   ```
   [TRAINING] Starting Atlan Auth SDK initialization...
   [TRAINING] ✅ Authentication successful!
   ```

## Testing Checklist

### ✅ Basic Functionality
- [ ] Setup test passes (all dependencies installed)
- [ ] Backend health check responds
- [ ] Frontend loads without errors
- [ ] Authentication redirects to Atlan login

### ✅ Standalone Mode
- [ ] Redirects to Atlan login
- [ ] Returns to app after login
- [ ] Shows user information
- [ ] Shows "standalone" mode
- [ ] Shows message about asset GUID not available

### ✅ Embedded Mode (if configured in Atlan)
- [ ] No login redirect
- [ ] Shows "embedded" mode
- [ ] Displays asset GUID
- [ ] Fetches and displays asset description
- [ ] Shows asset name and type

### ✅ Error Handling
- [ ] Stop backend - frontend shows error message
- [ ] Use wrong Atlan URL - shows authentication error
- [ ] Invalid asset GUID - shows "not found" error

## Debug Tips

### Check Browser Console
Look for messages prefixed with `[TRAINING]`:
```javascript
[TRAINING] Starting Atlan Auth SDK initialization...
[TRAINING] Fetching asset details for GUID: abc-123
```

### Check Backend Logs
```
[INFO] [TRAINING] Health check requested
[INFO] [TRAINING] Received request for asset: abc-123
[INFO] [TRAINING] Found asset: MyTable (Type: Table)
```

### Common Issues

#### "Authentication failed"
- **Fix**: Ensure Atlan URL is correct and accessible
- **Check**: Can you access `https://your-tenant.atlan.com` in browser?

#### "Error loading asset details"
- **Fix**: Ensure backend is running on port 5000
- **Check**: `curl http://localhost:5000/api/health`

#### CORS Error
- **Fix**: Make sure both frontend and backend are running
- **Check**: Backend console for CORS configuration

#### "Asset not found"
- **Fix**: Only works with valid asset GUIDs in embedded mode
- **Check**: Backend logs for the actual GUID received

## Test with Different Assets

When running in embedded mode, test with various asset types:

1. **Table**: Should show database name, schema, description
2. **Column**: Should show data type, table name
3. **Glossary Term**: Should show glossary name
4. **Dashboard**: Should show dashboard type

## Performance Testing

1. **Initial Load Time**: Should authenticate within 2-3 seconds
2. **Asset Fetch Time**: Should load description within 1-2 seconds
3. **Token Refresh**: SDK handles automatically (test by waiting 15+ minutes)

## Success Criteria

The training example is working correctly if:

✅ **Standalone Mode**:
- Authenticates via Keycloak redirect
- Shows user information
- Indicates standalone mode

✅ **Embedded Mode**:
- No authentication redirect
- Shows asset GUID from Atlan
- Fetches and displays asset description

✅ **Both Modes**:
- Clean, readable display
- No console errors
- Clear error messages when things fail

---

## Quick Commands Reference

```bash
# Test setup
python test_setup.py

# Start backend
python backend.py

# Start frontend
python -m http.server 8000

# Test backend health
curl http://localhost:5000/api/health

# Open in browser
open http://localhost:8000  # macOS
xdg-open http://localhost:8000  # Linux
start http://localhost:8000  # Windows
```