#!/bin/bash

# Test script for home.atlan.com API token
echo "Testing API token for home.atlan.com"
echo "======================================"
echo ""

# Replace this with your actual token from home.atlan.com
TOKEN="YOUR_HOME_ATLAN_TOKEN_HERE"

if [ "$TOKEN" = "YOUR_HOME_ATLAN_TOKEN_HERE" ]; then
    echo "⚠️  Please edit this script and add your API token from home.atlan.com"
    exit 1
fi

echo "Testing /api/meta/user/current endpoint..."
response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "https://home.atlan.com/api/meta/user/current")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    echo "✅ API token is valid!"
    echo ""
    echo "User info:"
    echo "$body" | jq -r '.username, .email, .firstName, .lastName' 2>/dev/null || echo "$body"
else
    echo "❌ API call failed with HTTP $http_code"
    echo "$body"
fi

echo ""
echo "Testing token expiry..."
payload=$(echo "$TOKEN" | cut -d. -f2)
if [ ! -z "$payload" ]; then
    decoded=$(echo "$payload" | base64 -d 2>/dev/null)
    if [ ! -z "$decoded" ]; then
        exp=$(echo "$decoded" | grep -o '"exp":[0-9]*' | cut -d: -f2)
        if [ ! -z "$exp" ]; then
            exp_date=$(date -r "$exp" 2>/dev/null || date -d "@$exp" 2>/dev/null)
            echo "Token expires: $exp_date"
        fi
    fi
fi