# Atlan OAuth Example (SDR Mode)

This example demonstrates OAuth 2.0 with PKCE flow for Atlan's SDR (Self-Deployed Runtime) mode. It runs entirely in Docker, so no Node.js installation is required on your machine.

## Overview

This application demonstrates:
- OAuth 2.0 Authorization Code flow with PKCE
- Token exchange and storage
- Making authenticated API calls to Atlan
- Token refresh mechanism (if refresh tokens are available)

## Prerequisites

- Docker and Docker Compose installed on your machine
- Access to an Atlan instance
- OAuth client credentials from your Atlan instance

## Quick Start

### 1. Clone/Copy the Files

Navigate to the oauth-example directory:
```bash
cd /Users/gene.arnold/WorkSpace/atlan-iframe/oauth-example
```

### 2. Configure Environment Variables

Copy the example environment file and edit it with your Atlan instance details:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual values:

```env
# Your Atlan instance URL
ATLAN_INSTANCE_URL=https://your-instance.atlan.com

# OAuth Client ID (required)
OAUTH_CLIENT_ID=your-client-id

# OAuth endpoints (update with your instance URL)
OAUTH_AUTH_ENDPOINT=https://your-instance.atlan.com/auth/realms/default/protocol/openid-connect/auth
OAUTH_TOKEN_ENDPOINT=https://your-instance.atlan.com/auth/realms/default/protocol/openid-connect/token

# Leave as-is for local testing
OAUTH_REDIRECT_URI=http://localhost:3000/callback
```

### 3. Start the Application with Docker

Build and run the application:

```bash
docker-compose up --build
```

Or run in the background:

```bash
docker-compose up -d --build
```

### 4. Test the OAuth Flow

1. Open your browser and navigate to: http://localhost:3000
2. Click "Start OAuth Flow"
3. You'll be redirected to your Atlan instance to login
4. After successful authentication, you'll be redirected back to the success page
5. The success page will show your tokens and allow you to test API calls

## Finding Your OAuth Endpoints

For Keycloak-based Atlan instances, the OAuth endpoints typically follow this pattern:

```
Authorization: https://{instance}/auth/realms/{realm}/protocol/openid-connect/auth
Token:         https://{instance}/auth/realms/{realm}/protocol/openid-connect/token
```

You can usually find the complete configuration at:
```
https://{instance}/auth/realms/{realm}/.well-known/openid-configuration
```

## Troubleshooting

### "Invalid client" or "Client not found" Error

This means your `OAUTH_CLIENT_ID` is incorrect. Verify:
- The client ID matches exactly what's registered in Atlan
- The client is enabled in Keycloak/Atlan

### "Invalid redirect URI" Error

The redirect URI must match EXACTLY what's registered in your OAuth client configuration:
- Check for trailing slashes
- Ensure the protocol matches (http vs https)
- Port number must match (3000)

### "PKCE code challenge required" Error

This is good! It means PKCE is enforced. Our code handles this automatically.

### "Unauthorized grant type" Error

Your client may not be configured for the authorization_code grant type. This needs to be enabled in the OAuth client configuration.

### Connection Refused

Make sure:
- Docker is running
- Port 3000 is not already in use
- The container started successfully (`docker-compose logs`)

## How It Works

1. **PKCE Generation**: The app generates a random code verifier and its SHA256 hash (code challenge)
2. **Authorization Request**: User is redirected to Atlan with the code challenge
3. **User Authentication**: User logs in via Atlan's login page
4. **Authorization Code**: Atlan redirects back with an authorization code
5. **Token Exchange**: App exchanges the code + code verifier for tokens
6. **API Access**: App can now make authenticated requests to Atlan's API

## Project Structure

```
oauth-example/
├── server.js           # Express server with OAuth flow
├── public/
│   ├── index.html     # Landing page
│   └── success.html   # Success page showing tokens
├── Dockerfile         # Container configuration
├── docker-compose.yml # Docker compose configuration
├── package.json       # Node.js dependencies
├── .env.example       # Environment variables template
├── .env              # Your actual configuration (not committed)
└── README.md         # This file
```

## Security Notes

- Never commit your `.env` file with real credentials
- The session secret should be changed in production
- PKCE provides protection against authorization code interception
- Tokens are stored in server-side sessions, not client-side

## Useful Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Clean up everything (including volumes)
docker-compose down -v

# Access the container shell
docker-compose exec oauth-app sh
```

## Next Steps

Once you have OAuth working:

1. **Test Token Refresh**: If your client has offline_access scope, test refresh token flow
2. **Add Token Persistence**: Store tokens in a database for production use
3. **Implement Token Expiry Handling**: Automatically refresh tokens before they expire
4. **Add to iframe**: Once OAuth works standalone, integrate into the iframe postMessage flow

## Common Atlan API Endpoints to Test

Once authenticated, you can test these endpoints:

```
GET /api/meta/user/current          # Current user info
GET /api/meta/entity/guid/{guid}    # Get asset by GUID
GET /api/meta/search/basic          # Search assets
```

## Need Help?

1. Check the container logs: `docker-compose logs`
2. Verify your OAuth endpoints are correct
3. Ensure your client is properly configured in Atlan/Keycloak
4. Try the flow in an incognito window to avoid cookie issues