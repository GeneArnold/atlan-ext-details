# 🚀 Deploy to Render for Atlan External Tab

## Quick Deploy (5 minutes)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add production files for Render deployment"
git push
```

### Step 2: Deploy to Render

#### Option A: Using Render Dashboard

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo: `GeneArnold/atlan-ext-details`
4. Configure:
   - **Name**: `atlan-external-tab` (or any name you want)
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free (or Starter for production)
5. Click **"Create Web Service"**

#### Option B: Using render.yaml (Automatic)

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repo
4. Render will detect the `render.yaml` and configure automatically
5. Click **"Apply"**

### Step 3: Wait for Deployment

- Takes about 3-5 minutes
- You'll see build logs in real-time
- Once complete, you'll get a URL like: `https://atlan-external-tab.onrender.com`

## 🔧 Configure in Atlan

### Add as External Tab in Atlan

1. **Login to Atlan** (partner-sandbox.atlan.com)
2. **Go to Admin** → **Workspace** → **External Tabs** (or similar)
3. **Add New Tab**:
   - **Name**: External Details
   - **URL**: `https://your-app-name.onrender.com`
   - **Location**: Asset Profile Tab
   - **Icon**: Choose any icon
4. **Save**

### Register OAuth Redirect URI

**IMPORTANT**: For OAuth to work, an Atlan admin needs to:

1. Go to OAuth/SSO settings in Atlan
2. Add your Render URL as allowed redirect:
   - `https://your-app-name.onrender.com`
   - `https://your-app-name.onrender.com/*`

## ✅ Testing Your Deployment

### 1. Test Health Endpoint
```bash
curl https://your-app-name.onrender.com/health
```

Should return:
```json
{"status": "healthy", "service": "atlan-external-tab"}
```

### 2. Test in Atlan
1. Navigate to any asset in Atlan
2. Click on your "External Details" tab
3. You should see:
   - User information (OAuth working)
   - Asset GUID (postMessage working)
   - Asset description (pyatlan SDK working)

## 🎯 What You Get

Once deployed, your external tab will:

1. **Authenticate users** automatically using Atlan Auth SDK
2. **Display user information** (proves OAuth is working)
3. **Show asset GUID** (proves iframe communication works)
4. **Fetch and display asset description** (proves API integration works)

## 📝 Environment Variables (Optional)

In Render dashboard, you can add:

- `ATLAN_BASE_URL`: Change if using different Atlan instance
- `PORT`: Render sets this automatically

## 🐛 Troubleshooting

### "redirect_uri invalid" Error
- The Render URL needs to be registered in Atlan's OAuth settings
- Contact Atlan admin to add: `https://your-app-name.onrender.com`

### "Not authenticated" in Atlan
- Make sure you're logged into Atlan first
- Try refreshing the page
- Check browser console for errors

### Asset details not loading
- Check if you're on an actual asset page
- Verify the backend is running (check /health endpoint)
- Look at Render logs for errors

### Slow initial load
- Free tier on Render spins down after 15 minutes of inactivity
- First request takes ~30 seconds to spin up
- Consider upgrading to paid tier for always-on service

## 📊 What Success Looks Like

When everything works, you'll see:

```
External Details Tab
━━━━━━━━━━━━━━━━━━━

🔐 Authentication Status
   Status: Authenticated ✓
   Mode: embedded

👤 User Information
   Username: your.name
   Email: your.email@company.com
   Full Name: Your Name

📄 Asset Information
   Asset GUID: abc-123-def-456
   Name: Customer Table
   Type: Table
   Description: Table containing customer data
   Qualified Name: default/snowflake/db/schema/table
```

## 🎉 Done!

Your Atlan external tab is now live on Render and integrated with Atlan!

**Your URL**: `https://your-app-name.onrender.com`

**Next Steps**:
1. Test with different asset types
2. Add more fields to display
3. Customize the styling
4. Add more functionality

---

## Files Deployed

- `app.py` - Combined Flask backend + frontend server
- `templates/index.html` - The UI
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `Procfile` - Alternative deployment config

All the training example code is still in `/training-example` for reference, but Render uses the root files.