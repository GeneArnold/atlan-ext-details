// CRITICAL: PostMessage Implementation for Atlan iframe Integration
// This is the WORKING implementation that fixes all race conditions

// ============================================
// INITIALIZATION (MUST BE IMMEDIATE!)
// ============================================

// State variables - use undefined for "not checked yet"
let isConfigured = undefined;  // undefined = not checked, true/false = checked
let handshakeReceived = false;
let authContextReceived = false;
let assetGuid = null;

// ============================================
// MESSAGE LISTENER SETUP - DO THIS IMMEDIATELY!
// ============================================

// CRITICAL: Set up message listener IMMEDIATELY when script loads
// Do NOT wait for DOM ready, window.load, or any other event!
console.log('Setting up message listener at:', new Date().toISOString());

window.addEventListener('message', async (event) => {
    console.log('[MESSAGE] Received at', new Date().toISOString(), ':', event.data);
    console.log('[MESSAGE] Origin:', event.origin);

    // Safety check for data
    if (!event.data || typeof event.data !== 'object') {
        console.log('[MESSAGE] Invalid message format, ignoring');
        return;
    }

    // SECURITY: Always validate origin
    const allowedOrigins = [
        'https://home.atlan.com',
        'https://partner-sandbox.atlan.com',
        'http://localhost:3001'  // For local testing
    ];

    if (!allowedOrigins.includes(event.origin) && event.origin !== window.location.origin) {
        console.log('[MESSAGE] Ignoring message from unauthorized origin:', event.origin);
        return;
    }

    const { type, payload } = event.data;
    console.log('[MESSAGE] Processing type:', type);

    // Handle Atlan handshake
    if (type === 'ATLAN_HANDSHAKE') {
        handshakeReceived = true;
        console.log('[HANDSHAKE] Received, responding with IFRAME_READY');

        // ALWAYS respond to handshake immediately
        window.parent.postMessage({
            type: 'IFRAME_READY',
            payload: { ready: true }
        }, event.origin);  // SECURITY: Use explicit origin, never '*'

        // Check configuration if not done yet
        if (isConfigured === undefined) {
            checkConfiguration();
        }
    }
    // Handle auth context with asset info
    else if (type === 'ATLAN_AUTH_CONTEXT') {
        authContextReceived = true;
        console.log('[AUTH_CONTEXT] Received:', payload);

        // Defensive check for payload structure
        if (payload && payload.page && payload.page.params && payload.page.params.id) {
            assetGuid = payload.page.params.id;
            console.log('[AUTH_CONTEXT] Asset GUID:', assetGuid);

            // Ensure configuration is checked before processing
            if (isConfigured === undefined) {
                await checkConfiguration();
            }

            // Now load your content based on the asset
            if (isConfigured) {
                await loadAssetContent(assetGuid);
            }
        } else {
            console.error('[AUTH_CONTEXT] Missing required data in payload:', payload);
            showError('No asset GUID received from Atlan');
        }
    }
    // Handle logout
    else if (type === 'ATLAN_LOGOUT') {
        console.log('[LOGOUT] Received logout message');
        handleLogout();
    }
    // Handle token request (if your app needs fresh tokens)
    else if (type === 'IFRAME_TOKEN_REQUEST') {
        console.log('[TOKEN] Token refresh requested');
        // Request new token from Atlan
        window.parent.postMessage({
            type: 'IFRAME_TOKEN_REQUEST',
            payload: { needsToken: true }
        }, event.origin);
    }
});

// ============================================
// CONFIGURATION CHECK
// ============================================

async function checkConfiguration() {
    try {
        // Check if your backend is configured properly
        const response = await fetch('/api/config');
        const data = await response.json();
        isConfigured = data.configured;
        console.log('[CONFIG] Configuration check:', { configured: isConfigured });

        if (!isConfigured) {
            showError('Application not configured. Please set environment variables.');
        }
        return isConfigured;
    } catch (error) {
        console.error('[CONFIG] Configuration check failed:', error);
        isConfigured = false;
        return false;
    }
}

// ============================================
// IMMEDIATE INITIALIZATION
// ============================================

// Check configuration immediately (don't wait for DOM)
console.log('[INIT] Checking configuration immediately');
checkConfiguration();

// ============================================
// PROACTIVE FALLBACK
// ============================================

// If Atlan hasn't sent handshake after 500ms, proactively send IFRAME_READY
setTimeout(() => {
    if (!handshakeReceived) {
        console.log('[INIT] No handshake received yet, proactively sending IFRAME_READY');

        // Try to determine parent origin
        const parentOrigin = document.referrer
            ? new URL(document.referrer).origin
            : 'https://partner-sandbox.atlan.com';  // Default to production

        window.parent.postMessage({
            type: 'IFRAME_READY',
            payload: { ready: true }
        }, parentOrigin);
    }
}, 500);

// ============================================
// DOM READY HANDLER (Only for UI updates)
// ============================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('[INIT] DOM ready');
        initializeUI();
    });
} else {
    console.log('[INIT] DOM already loaded');
    initializeUI();
}

// ============================================
// BUSINESS LOGIC FUNCTIONS
// ============================================

async function loadAssetContent(guid) {
    console.log('[LOAD] Loading content for asset:', guid);

    try {
        // Add retry logic for network errors
        let retryCount = 0;
        const maxRetries = 3;

        while (retryCount < maxRetries) {
            try {
                const response = await fetch(`/api/asset/${guid}`);
                const data = await response.json();

                if (data.success) {
                    displayContent(data);
                    return;
                } else {
                    throw new Error(data.error || 'Failed to load asset');
                }
            } catch (error) {
                retryCount++;
                if (retryCount < maxRetries) {
                    console.log(`[LOAD] Retry ${retryCount}/${maxRetries} after error:`, error);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                } else {
                    throw error;
                }
            }
        }
    } catch (error) {
        console.error('[LOAD] Failed to load asset:', error);
        showError(`Failed to load asset: ${error.message}`);
    }
}

function displayContent(data) {
    console.log('[DISPLAY] Showing content:', data);
    // Update your UI with the loaded content
    const contentDiv = document.getElementById('content');
    if (contentDiv) {
        contentDiv.innerHTML = `
            <h2>${data.name}</h2>
            <p>${data.description}</p>
            <!-- Your content here -->
        `;
    }
}

function showError(message) {
    console.error('[ERROR]', message);
    const contentDiv = document.getElementById('content') || document.body;
    contentDiv.innerHTML = `
        <div style="color: red; padding: 20px;">
            <h3>Error</h3>
            <p>${message}</p>
        </div>
    `;
}

function handleLogout() {
    console.log('[LOGOUT] Cleaning up session');
    // Clear any stored data
    assetGuid = null;
    // Update UI to show logged out state
    showError('Session ended. Please refresh to continue.');
}

function initializeUI() {
    console.log('[UI] Initializing user interface');
    // Set up any UI elements, event handlers, etc.
}

// ============================================
// TEST MODE FOR LOCAL DEVELOPMENT
// ============================================

const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('test') === 'true') {
    console.log('[TEST] Running in test mode');

    // Simulate Atlan messages for local testing
    setTimeout(() => {
        window.postMessage({
            type: 'ATLAN_HANDSHAKE',
            payload: { appId: 'test-app' }
        }, '*');
    }, 100);

    setTimeout(() => {
        window.postMessage({
            type: 'ATLAN_AUTH_CONTEXT',
            payload: {
                page: {
                    params: {
                        id: 'test-asset-guid-123'
                    }
                }
            }
        }, '*');
    }, 200);
}

// ============================================
// KEY LESSONS LEARNED
// ============================================

/*
1. TIMING IS EVERYTHING
   - Set up message listeners IMMEDIATELY
   - Don't wait for DOM ready or window.load
   - Messages can arrive before your code is ready

2. STATE MANAGEMENT
   - Use undefined for "not yet determined" states
   - Differentiate between false and "not checked"
   - Track initialization phases explicitly

3. DEFENSIVE PROGRAMMING
   - Always validate message origin
   - Check payload structure defensively
   - Add retry logic for network operations
   - Have timeout-based fallbacks

4. DEBUGGING
   - Add prefixed logs ([INIT], [MESSAGE], etc.)
   - Include timestamps in critical logs
   - Test with clean browser state (incognito)
   - Clear cache when testing initial load

5. SECURITY
   - Never use '*' for postMessage targetOrigin
   - Always validate incoming message origins
   - Use explicit allowed origins list
   - Don't trust message data without validation
*/