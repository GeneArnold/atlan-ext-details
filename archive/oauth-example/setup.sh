#!/bin/bash

echo "================================================"
echo "  Atlan OAuth Example Setup"
echo "================================================"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "✓ .env file already exists"
    echo ""
    read -p "Do you want to reconfigure? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing configuration."
        echo ""
    else
        cp .env.example .env
        echo "✓ Reset .env from .env.example"
        echo ""
    fi
else
    cp .env.example .env
    echo "✓ Created .env from .env.example"
    echo ""
fi

# Prompt for Atlan instance
echo "Please provide your Atlan instance information:"
echo ""
read -p "Atlan instance URL (e.g., https://your-instance.atlan.com): " ATLAN_URL

# Remove trailing slash if present
ATLAN_URL=${ATLAN_URL%/}

# Update .env file
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|ATLAN_INSTANCE_URL=.*|ATLAN_INSTANCE_URL=$ATLAN_URL|" .env
    sed -i '' "s|OAUTH_AUTH_ENDPOINT=.*|OAUTH_AUTH_ENDPOINT=$ATLAN_URL/auth/realms/default/protocol/openid-connect/auth|" .env
    sed -i '' "s|OAUTH_TOKEN_ENDPOINT=.*|OAUTH_TOKEN_ENDPOINT=$ATLAN_URL/auth/realms/default/protocol/openid-connect/token|" .env
else
    # Linux
    sed -i "s|ATLAN_INSTANCE_URL=.*|ATLAN_INSTANCE_URL=$ATLAN_URL|" .env
    sed -i "s|OAUTH_AUTH_ENDPOINT=.*|OAUTH_AUTH_ENDPOINT=$ATLAN_URL/auth/realms/default/protocol/openid-connect/auth|" .env
    sed -i "s|OAUTH_TOKEN_ENDPOINT=.*|OAUTH_TOKEN_ENDPOINT=$ATLAN_URL/auth/realms/default/protocol/openid-connect/token|" .env
fi

echo "✓ Updated Atlan instance URL"
echo ""

# Prompt for Client ID
read -p "OAuth Client ID: " CLIENT_ID

if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|OAUTH_CLIENT_ID=.*|OAUTH_CLIENT_ID=$CLIENT_ID|" .env
else
    sed -i "s|OAUTH_CLIENT_ID=.*|OAUTH_CLIENT_ID=$CLIENT_ID|" .env
fi

echo "✓ Updated OAuth Client ID"
echo ""

# Optional: Client Secret
read -p "OAuth Client Secret (press Enter to skip for PKCE-only): " CLIENT_SECRET

if [ ! -z "$CLIENT_SECRET" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|OAUTH_CLIENT_SECRET=.*|OAUTH_CLIENT_SECRET=$CLIENT_SECRET|" .env
    else
        sed -i "s|OAUTH_CLIENT_SECRET=.*|OAUTH_CLIENT_SECRET=$CLIENT_SECRET|" .env
    fi
    echo "✓ Updated OAuth Client Secret"
else
    echo "✓ Using PKCE without client secret"
fi

echo ""
echo "================================================"
echo "  Configuration Complete!"
echo "================================================"
echo ""
echo "You can view the OpenID configuration at:"
echo "$ATLAN_URL/auth/realms/default/.well-known/openid-configuration"
echo ""
echo "To start the application, run:"
echo "  docker-compose up --build"
echo ""
echo "Then open: http://localhost:3000"
echo ""