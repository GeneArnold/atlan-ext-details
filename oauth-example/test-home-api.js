const axios = require('axios');
require('dotenv').config();

async function testHomeAPI() {
  const token = process.env.HOME_API_TOKEN;
  const instance = 'https://home.atlan.com';

  if (!token) {
    console.error('❌ No HOME_API_TOKEN found in .env file');
    process.exit(1);
  }

  console.log('Testing Atlan API on home.atlan.com...\n');

  try {
    // Test search API
    console.log('1. Testing search API...');
    const searchResponse = await axios.post(`${instance}/api/meta/search/indexsearch`,
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

    console.log('✅ API call successful!');
    console.log(`Found ${searchResponse.data.approximateCount || 0} total assets`);

    if (searchResponse.data.entities && searchResponse.data.entities.length > 0) {
      const firstAsset = searchResponse.data.entities[0];
      console.log('\nFirst asset found:');
      console.log(`- Name: ${firstAsset.displayText || firstAsset.attributes?.name}`);
      console.log(`- Type: ${firstAsset.typeName}`);
      console.log(`- GUID: ${firstAsset.guid}`);
    }

    // Test types API
    console.log('\n2. Testing types API...');
    const typesResponse = await axios.get(`${instance}/api/meta/types/typedefs`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    console.log('✅ Types API works!');
    console.log(`Found ${typesResponse.data.entityDefs?.length || 0} entity types`);

  } catch (error) {
    console.error('❌ API test failed:');

    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Response:', JSON.stringify(error.response.data, null, 2));
    } else {
      console.error('Error:', error.message);
    }

    process.exit(1);
  }

  console.log('\n✅ All tests passed! Your API token is working with home.atlan.com');
}

testHomeAPI();