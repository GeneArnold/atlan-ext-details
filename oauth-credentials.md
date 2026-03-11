# OAuth Client Credentials for Atlan

## ⚠️ IMPORTANT: Keep these credentials secure!

These credentials are for OAuth authentication with the Atlan instance at:
`https://partner-sandbox.atlan.com`

## OAuth Client Details

- **Client ID**: `oauth-client-2ecb7cc0-08d1-43f3-9159-fceadbf0d739`
- **Client Secret**: `0ad25f4a-fcd1-4f2c-8806-38afe3ee3d51`
- **Grant Type**: Authorization Code with PKCE
- **Redirect URI**: `http://localhost:3000/callback`

## OAuth Endpoints

Based on the Atlan instance, the OAuth endpoints are:

- **Authorization Endpoint**:
  `https://partner-sandbox.atlan.com/auth/realms/default/protocol/openid-connect/auth`

- **Token Endpoint**:
  `https://partner-sandbox.atlan.com/auth/realms/default/protocol/openid-connect/token`

- **OpenID Configuration**:
  `https://partner-sandbox.atlan.com/auth/realms/default/.well-known/openid-configuration`

## Security Notes

1. **Never commit these credentials to version control**
2. The `.gitignore` file is configured to exclude `.env` files
3. In production, use environment variables or a secrets manager
4. These credentials should only be used for development/testing

## Setup Instructions

These credentials have been automatically added to your `.env` file in the oauth-example directory.

To test the OAuth flow:

```bash
cd /Users/gene.arnold/WorkSpace/atlan-iframe/oauth-example
docker-compose up --build
```

Then open http://localhost:3000 and click "Start OAuth Flow"

## Troubleshooting

If you get an "invalid redirect URI" error:
- The OAuth client must be configured to allow `http://localhost:3000/callback`
- Contact your Atlan administrator to add this redirect URI to the client configuration

## Token Information

The OAuth flow will provide:
- **Access Token**: For API calls (expires in ~15 minutes)
- **Refresh Token**: To get new access tokens (if offline_access scope is granted)
- **ID Token**: Contains user identity information