#!/usr/bin/env python3
"""
Debug script to test Atlan REST API and find where description is stored
"""

import requests
import json
import sys

# Configuration
ATLAN_BASE_URL = "https://fs3.atlan.com"
ASSET_GUID = "857d5dc4-8897-4c8e-beb7-55c2159a3533"  # SAMPLE_MC_TABLE

def test_asset_api(token):
    """
    Test the Atlan API and print the full response to find description field
    """
    api_url = f"{ATLAN_BASE_URL}/api/meta/entity/guid/{ASSET_GUID}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    print(f"Testing API: {api_url}")
    print("=" * 80)

    try:
        response = requests.get(api_url, headers=headers)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Save full response for analysis
            with open('asset_response_debug.json', 'w') as f:
                json.dump(data, f, indent=2)

            print("\n✅ Response saved to asset_response_debug.json")

            # Check different possible locations for description
            entity = data.get('entity', data)
            attributes = entity.get('attributes', {})

            print("\n📋 Checking for description in different locations:")
            print("-" * 40)

            # Check all attribute fields
            print("\n1. All attributes keys:")
            for key in attributes.keys():
                if 'desc' in key.lower() or 'summary' in key.lower():
                    print(f"   - {key}: {attributes[key][:100] if attributes[key] else 'None'}...")

            # Check specific fields
            fields_to_check = [
                'description',
                'userDescription',
                'businessDescription',
                'techDescription',
                'summary',
                'comment',
                'remarks',
                'details',
                'definition'
            ]

            print("\n2. Specific description fields:")
            for field in fields_to_check:
                value = attributes.get(field)
                if value:
                    print(f"   ✅ {field}: {value[:100]}...")
                else:
                    print(f"   ❌ {field}: Not found")

            # Check meanings
            print("\n3. Meanings/Glossary terms:")
            meanings = entity.get('meanings', [])
            if meanings:
                for i, meaning in enumerate(meanings):
                    print(f"   - Meaning {i}: {meaning.get('displayText', 'N/A')}")
            else:
                print("   No meanings found")

            # Check custom attributes
            print("\n4. Custom attributes:")
            custom_attrs = entity.get('customAttributes', {})
            if custom_attrs:
                for key, value in custom_attrs.items():
                    if 'desc' in key.lower():
                        print(f"   - {key}: {value}")
            else:
                print("   No custom attributes")

            # Check relationship attributes
            print("\n5. Relationship attributes:")
            rel_attrs = entity.get('relationshipAttributes', {})
            if rel_attrs:
                for key in rel_attrs.keys():
                    if 'desc' in key.lower() or 'readme' in key.lower():
                        print(f"   - {key}: Found")
            else:
                print("   No relationship attributes")

            # Print all top-level keys
            print("\n6. All top-level entity keys:")
            for key in entity.keys():
                print(f"   - {key}")

            print("\n" + "=" * 80)
            print("Check asset_response_debug.json for full response structure")

        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # You need to pass the OAuth token as argument
    if len(sys.argv) < 2:
        print("Usage: python debug_asset_api.py <oauth_token>")
        print("\nTo get token:")
        print("1. Open browser DevTools on the External Details tab")
        print("2. In Console, type: authContext.token")
        print("3. Copy the token and run: python debug_asset_api.py <token>")
        sys.exit(1)

    token = sys.argv[1]
    test_asset_api(token)