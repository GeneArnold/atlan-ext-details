const axios = require('axios');
require('dotenv').config();

// This script tests the API token directly (not OAuth)
async function testAPIToken() {
  const token = process.env.API_TOKEN;
  const atlanInstance = process.env.ATLAN_INSTANCE_URL;

  if (!token) {
    console.error('❌ No API_TOKEN found in .env file');
    process.exit(1);
  }

  if (!atlanInstance) {
    console.error('❌ No ATLAN_INSTANCE_URL found in .env file');
    process.exit(1);
  }

  console.log('Testing API token against Atlan instance...');
  console.log('Instance:', atlanInstance);
  console.log('');

  try {
    // Test 1: Get current user info
    console.log('1. Testing /api/meta/user/current...');
    const userResponse = await axios.get(`${atlanInstance}/api/meta/user/current`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json'
      }
    });

    console.log('✅ Successfully authenticated!');
    console.log('User info:', JSON.stringify(userResponse.data, null, 2));
    console.log('');

    // Test 2: Basic search
    console.log('2. Testing /api/meta/search/basic...');
    const searchResponse = await axios.post(`${atlanInstance}/api/meta/search/basic`,
      {
        dsl: {
          size: 1,
          from: 0
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    console.log('✅ Search API works!');
    console.log(`Found ${searchResponse.data.searchParameters?.size || 0} results`);
    console.log('');

    // Decode the token to show details
    console.log('3. Token details:');
    const payload = token.split('.')[1];
    const decoded = JSON.parse(Buffer.from(payload, 'base64').toString());

    console.log('- Client ID:', decoded.azp || decoded.client_id);
    console.log('- Username:', decoded.preferred_username || decoded.username);
    console.log('- Issued at:', new Date(decoded.iat * 1000).toLocaleString());
    console.log('- Expires at:', new Date(decoded.exp * 1000).toLocaleString());
    console.log('- Realm:', decoded.realm || 'default');
    console.log('');

    console.log('✅ All tests passed! The API token is valid and working.');

  } catch (error) {
    console.error('❌ API test failed:');

    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Status Text:', error.response.statusText);
      console.error('Response:', error.response.data);
    } else {
      console.error('Error:', error.message);
    }

    // Check if token is expired
    try {
      const payload = token.split('.')[1];
      const decoded = JSON.parse(Buffer.from(payload, 'base64').toString());
      const expiry = new Date(decoded.exp * 1000);

      if (expiry < new Date()) {
        console.error('');
        console.error('⚠️  Token expired on:', expiry.toLocaleString());
        console.error('You need to generate a new API token.');
      }
    } catch (e) {
      // Ignore decoding errors
    }

    process.exit(1);
  }
}

// Run the test
testAPIToken();