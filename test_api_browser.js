// Run this in browser console from External Details tab to debug API response

async function testAssetAPI() {
    const guid = '857d5dc4-8897-4c8e-beb7-55c2159a3533';
    const token = authContext.token;

    console.log('🔍 Testing Atlan API for asset:', guid);

    try {
        const response = await fetch(`/api/asset/${guid}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        console.log('📦 Backend response:', data);

        // Now test direct API
        console.log('\n🔍 Testing direct Atlan API...');

        const directResponse = await fetch(`https://fs3.atlan.com/api/meta/entity/guid/${guid}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const directData = await directResponse.json();
        console.log('📦 Direct API response:', directData);

        // Check for description in different places
        const entity = directData.entity || directData;
        const attributes = entity.attributes || {};

        console.log('\n📋 Checking for description fields:');
        console.log('attributes.description:', attributes.description);
        console.log('attributes.userDescription:', attributes.userDescription);
        console.log('attributes.businessDescription:', attributes.businessDescription);
        console.log('attributes.comment:', attributes.comment);
        console.log('attributes.remarks:', attributes.remarks);

        // Check all attribute keys
        console.log('\n📋 All attribute keys:');
        Object.keys(attributes).forEach(key => {
            if (key.toLowerCase().includes('desc') ||
                key.toLowerCase().includes('comment') ||
                key.toLowerCase().includes('summary')) {
                console.log(`  - ${key}:`, attributes[key]);
            }
        });

        // Check for readme
        console.log('\n📋 Checking relationship attributes:');
        const relAttrs = entity.relationshipAttributes || {};
        if (relAttrs.readme) {
            console.log('  - readme found:', relAttrs.readme);
        }
        if (relAttrs.meanings) {
            console.log('  - meanings found:', relAttrs.meanings);
        }

        return directData;

    } catch (error) {
        console.error('❌ Error:', error);
    }
}

// Run the test
testAssetAPI();