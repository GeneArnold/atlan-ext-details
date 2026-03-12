// ============================================
// CONFIGURATION FILE FOR ATLAN TRAINING EXAMPLE
// ============================================
//
// Instructions:
// 1. Copy this file to 'config.js'
// 2. Update the values below with your actual Atlan instance details
// 3. The config.js file is ignored by git for security

// Your Atlan instance URL
// Example: If you access Atlan at https://mycompany.atlan.com
// Then use: 'https://mycompany.atlan.com'
const ATLAN_CONFIG = {
    // Your Atlan instance URL (using partner sandbox for training)
    ATLAN_INSTANCE_URL: 'https://partner-sandbox.atlan.com',

    // Backend API endpoint (usually doesn't need to change)
    BACKEND_URL: 'http://localhost:5000',

    // Frontend server port (change if 8000 is in use)
    FRONTEND_PORT: 8000
};

// Export for use in other files (if using modules)
// For this training example, we'll use it directly in the HTML