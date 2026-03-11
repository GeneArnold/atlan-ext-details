const express = require('express');
const session = require('express-session');
const crypto = require('crypto');
const axios = require('axios');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Configuration from environment variables
const config = {
  clientId: process.env.OAUTH_CLIENT_ID,
  clientSecret: process.env.OAUTH_CLIENT_SECRET, // May not be needed for PKCE public clients
  redirectUri: process.env.OAUTH_REDIRECT_URI || `http://localhost:${PORT}/callback`,
  authorizationEndpoint: process.env.OAUTH_AUTH_ENDPOINT,
  tokenEndpoint: process.env.OAUTH_TOKEN_ENDPOINT,
  scope: process.env.OAUTH_SCOPE || 'openid profile email',
  atlanInstance: process.env.ATLAN_INSTANCE_URL
};

// Session configuration
app.use(session({
  secret: process.env.SESSION_SECRET || 'dev-secret-change-in-production',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false } // Set to true in production with HTTPS
}));

// Serve static files
app.use(express.static('public'));
app.use(express.json());

// PKCE Helper Functions
function base64URLEncode(str) {
  return str.toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

function generateCodeVerifier() {
  return base64URLEncode(crypto.randomBytes(32));
}

function generateCodeChallenge(verifier) {
  return base64URLEncode(crypto.createHash('sha256').update(verifier).digest());
}

// Homepage
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Initiate OAuth flow
app.get('/auth/login', (req, res) => {
  // Generate PKCE parameters
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = generateCodeChallenge(codeVerifier);
  const state = crypto.randomBytes(16).toString('hex');

  // Store in session for later verification
  req.session.codeVerifier = codeVerifier;
  req.session.state = state;

  // Build authorization URL
  const params = new URLSearchParams({
    client_id: config.clientId,
    response_type: 'code',
    redirect_uri: config.redirectUri,
    scope: config.scope,
    state: state,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256'
  });

  const authUrl = `${config.authorizationEndpoint}?${params.toString()}`;

  console.log('Redirecting to:', authUrl);
  res.redirect(authUrl);
});

// OAuth callback
app.get('/callback', async (req, res) => {
  const { code, state, error, error_description } = req.query;

  // Handle errors
  if (error) {
    console.error('OAuth error:', error, error_description);
    return res.status(400).send(`
      <html>
        <body>
          <h1>Authentication Error</h1>
          <p>Error: ${error}</p>
          <p>Description: ${error_description || 'No description provided'}</p>
          <a href="/">Try Again</a>
        </body>
      </html>
    `);
  }

  // Verify state
  if (state !== req.session.state) {
    console.error('State mismatch');
    return res.status(400).send('State mismatch - possible CSRF attack');
  }

  // Exchange authorization code for tokens
  try {
    const tokenData = {
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: config.redirectUri,
      client_id: config.clientId,
      code_verifier: req.session.codeVerifier
    };

    // If client secret is required (not typical for PKCE public clients)
    if (config.clientSecret) {
      tokenData.client_secret = config.clientSecret;
    }

    console.log('Exchanging code for token at:', config.tokenEndpoint);

    const tokenResponse = await axios.post(config.tokenEndpoint,
      new URLSearchParams(tokenData).toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );

    const tokens = tokenResponse.data;

    // Store tokens in session
    req.session.tokens = tokens;
    req.session.authenticated = true;

    // Decode ID token if present (just for display, not verification)
    let userInfo = {};
    if (tokens.id_token) {
      try {
        const payload = tokens.id_token.split('.')[1];
        userInfo = JSON.parse(Buffer.from(payload, 'base64').toString());
      } catch (e) {
        console.error('Error decoding ID token:', e);
      }
    }

    // Redirect to success page
    res.redirect('/success');

  } catch (error) {
    console.error('Token exchange error:', error.response?.data || error.message);
    res.status(500).send(`
      <html>
        <body>
          <h1>Token Exchange Failed</h1>
          <pre>${JSON.stringify(error.response?.data || error.message, null, 2)}</pre>
          <a href="/">Try Again</a>
        </body>
      </html>
    `);
  }
});

// Success page
app.get('/success', (req, res) => {
  if (!req.session.authenticated) {
    return res.redirect('/');
  }

  res.sendFile(path.join(__dirname, 'public', 'success.html'));
});

// API endpoint to get token info
app.get('/api/tokens', (req, res) => {
  if (!req.session.authenticated) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  res.json({
    tokens: req.session.tokens,
    session: {
      authenticated: req.session.authenticated
    }
  });
});

// Test Atlan API with token
app.get('/api/test-atlan', async (req, res) => {
  if (!req.session.authenticated || !req.session.tokens?.access_token) {
    return res.status(401).json({ error: 'Not authenticated' });
  }

  try {
    // Try to call Atlan's user info endpoint
    const response = await axios.get(`${config.atlanInstance}/api/meta/user/current`, {
      headers: {
        'Authorization': `Bearer ${req.session.tokens.access_token}`
      }
    });

    res.json({
      success: true,
      user: response.data
    });
  } catch (error) {
    res.status(error.response?.status || 500).json({
      success: false,
      error: error.response?.data || error.message
    });
  }
});

// Logout
app.get('/auth/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`OAuth example server running at http://localhost:${PORT}`);
  console.log('\nConfiguration:');
  console.log('- Client ID:', config.clientId || 'NOT SET');
  console.log('- Authorization Endpoint:', config.authorizationEndpoint || 'NOT SET');
  console.log('- Token Endpoint:', config.tokenEndpoint || 'NOT SET');
  console.log('- Redirect URI:', config.redirectUri);
  console.log('- Atlan Instance:', config.atlanInstance || 'NOT SET');
});