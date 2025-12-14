const axios = require('axios');

async function testApi() {
    try {
        const response = await axios.get('http://127.0.0.1:5001/api/data/cleaned?limit=5');
        console.log('Response Status:', response.status);
        console.log('Response Keys:', Object.keys(response));
        console.log('Response Data Type:', typeof response.data);
        console.log('Response Data Is Array:', Array.isArray(response.data));
        console.log('Response Data Keys:', Object.keys(response.data));
        if (!Array.isArray(response.data)) {
            console.log('Response Data.data Type:', typeof response.data.data);
            if (response.data.data && response.data.data.length > 0) {
                console.log('First Item:', JSON.stringify(response.data.data[0], null, 2));
            }
        } else {
            if (response.data.length > 0) {
                console.log('First Item:', JSON.stringify(response.data[0], null, 2));
            }
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

testApi();
