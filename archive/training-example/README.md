# Atlan External Tab Integration - Training Example

## 🎯 Purpose

This training example demonstrates how to build an external tab integration for Atlan using modern tools:
- **Atlan Auth SDK** for simple authentication
- **pyatlan SDK** for fetching asset data
- **PostMessage protocol** for iframe communication

## 📚 What You'll Learn

1. **Authentication Flow**
   - How the Atlan Auth SDK handles both embedded (iframe) and standalone (localhost) modes
   - How OAuth tokens are passed between frontend and backend

2. **PostMessage Communication**
   - How Atlan passes the asset GUID to your tab via `page.params.id`
   - How the handshake works between Atlan and your application

3. **API Integration**
   - How to use pyatlan SDK to fetch asset details
   - How to pass tokens from frontend to backend securely

## 📁 Project Structure

```
training-example/
├── index.html        # Frontend with Atlan Auth SDK
├── backend.py        # Python backend with pyatlan SDK
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.8+** installed
2. **Atlan instance** URL (e.g., `https://your-tenant.atlan.com`)
3. **Access to Atlan** with a user account

### Step 1: Set Up Python Environment

#### Option A: Quick Setup (Recommended)
```bash
cd training-example
./setup.sh  # This creates venv and installs dependencies
```

#### Option B: Manual Setup
```bash
cd training-example

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Your Atlan Instance

The training example is pre-configured to use `https://partner-sandbox.atlan.com`.

If you need to use a different Atlan instance, edit `index.html` (line ~200):

```javascript
// Change this line:
const ATLAN_INSTANCE_URL = 'https://partner-sandbox.atlan.com';
// To your actual Atlan instance:
const ATLAN_INSTANCE_URL = 'https://your-company.atlan.com';
```

### Step 3: Set Environment Variable (Optional)

For the backend, the Atlan URL is already configured. If you need to change it:

```bash
export ATLAN_BASE_URL='https://partner-sandbox.atlan.com'
# Or for your own instance:
# export ATLAN_BASE_URL='https://your-company.atlan.com'
```

### Step 4: Start the Backend

```bash
# Make sure venv is activated
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Start the backend
python backend.py
```

You should see:
```
============================================================
ATLAN EXTERNAL TAB TRAINING BACKEND
============================================================
Starting Flask server...
Backend will be available at: http://localhost:5000
```

### Step 5: Start the Frontend

In a new terminal:

```bash
cd training-example
python -m http.server 8000
# Or use any other static file server:
# npx serve .
```

### Step 6: Test the Integration

#### Standalone Mode (Local Development)

1. Open `http://localhost:8000` in your browser
2. The Atlan Auth SDK will redirect you to login
3. After login, you'll see:
   - Your user information (proves OAuth works)
   - "Not available (standalone mode)" for asset GUID (expected)
   - Message to run inside Atlan for asset details

#### Embedded Mode (Inside Atlan)

1. Configure your app in Atlan as an external tab
2. Navigate to any asset in Atlan
3. Click your custom tab
4. You'll see:
   - Your user information
   - The asset's GUID (proves postMessage works)
   - The asset's description (proves pyatlan integration works)

## 🔍 How It Works

### Frontend Flow (`index.html`)

```javascript
1. Load Atlan Auth SDK from CDN
   ↓
2. Initialize AtlanAuth with your instance URL
   ↓
3. SDK detects mode (embedded vs standalone)
   ↓
4. In embedded: Receives token via postMessage
   In standalone: Redirects to Keycloak login
   ↓
5. Display user info and asset GUID
   ↓
6. Call backend to fetch asset description
```

### Backend Flow (`backend.py`)

```python
1. Receive request with asset GUID
   ↓
2. Extract JWT token from Authorization header
   ↓
3. Initialize pyatlan client with token
   ↓
4. Fetch asset details using client.asset.get_by_guid()
   ↓
5. Return asset information as JSON
```

## 📊 What Gets Displayed

The training example shows three key pieces of information:

### 1. Authentication Status
- Shows if authentication succeeded
- Displays mode (embedded or standalone)

### 2. User Information (from OAuth)
- Username
- Email
- Full name
- User ID

### 3. Asset Information (from postMessage + pyatlan)
- Asset GUID (received via postMessage)
- Asset name
- Asset type
- Asset description
- Qualified name

## 🧪 Testing Different Scenarios

### Test Authentication
1. Open in incognito mode to test fresh login
2. Check that user info displays correctly

### Test Asset Data
1. Try different asset types (tables, columns, glossary terms)
2. Verify descriptions load correctly

### Test Error Handling
1. Stop the backend and see the error message
2. Use an invalid Atlan URL to see auth errors

## 🐛 Troubleshooting

### "Authentication failed"
- Check your Atlan instance URL is correct
- Ensure you have access to the Atlan instance
- Check browser console for detailed error

### "Error loading asset details"
- Ensure backend is running on port 5000
- Check backend console for error messages
- Verify CORS is working (check browser console)

### "Asset not found"
- Only works in embedded mode (inside Atlan)
- Verify the asset has a description
- Check backend logs for the actual GUID received

## 📝 Key Code Sections to Study

### Frontend: Authentication Setup
Look at lines 150-170 in `index.html`:
```javascript
const atlan = new AtlanAuth({
    origin: 'https://your-tenant.atlan.com',
    onReady: (context) => { ... },
    onError: (error) => { ... }
});
```

### Frontend: Extracting Asset GUID
Line 185 in `index.html`:
```javascript
const assetGuid = authContext.page?.params?.id || 'Not available';
```

### Backend: Using pyatlan
Lines 95-110 in `backend.py`:
```python
asset = client.asset.get_by_guid(
    guid=guid,
    min_ext_info=False,
    ignore_relationships=False
)
```

## 🎓 Learning Objectives Checklist

After running this example, you should understand:

- [ ] How Atlan Auth SDK simplifies authentication
- [ ] The difference between embedded and standalone modes
- [ ] How asset GUIDs are passed via postMessage
- [ ] How to use OAuth tokens with pyatlan SDK
- [ ] How to structure a frontend/backend integration
- [ ] Basic error handling for external tabs

## 🚦 Next Steps

1. **Modify the example** - Add more asset fields to display
2. **Add error handling** - Improve error messages
3. **Try different assets** - Test with various asset types
4. **Build your own** - Create a custom tab for your use case

## 📚 Additional Resources

- [Atlan Auth SDK Documentation](https://www.npmjs.com/package/@atlanhq/atlan-auth)
- [pyatlan SDK Documentation](https://developer.atlan.com/sdk/python/index.html)
- [Atlan API Reference](https://developer.atlan.com/api/index.html)

## ❓ Questions?

This is a training example designed to be simple and educational.
For production implementations, consider:
- Proper error handling
- Caching strategies
- Security best practices
- Performance optimization

---

**Remember:** This is for learning, not production! Keep experimenting and asking questions.