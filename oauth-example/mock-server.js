const express = require('express');
const session = require('express-session');
const path = require('path');

const app = express();
const PORT = 3001;

// Session configuration
app.use(session({
  secret: 'mock-secret',
  resave: false,
  saveUninitialized: true
}));

app.use(express.static('public'));
app.use(express.json());

// Mock authorization endpoint
app.get('/auth/mock/authorize', (req, res) => {
  const { client_id, redirect_uri, state, code_challenge } = req.query;

  // Store PKCE challenge for later verification
  req.session.code_challenge = code_challenge;
  req.session.state = state;

  // Simulate login page
  res.send(`
    <html>
      <body style="font-family: Arial; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="background: white; padding: 30px; border-radius: 8px; max-width: 400px; margin: 0 auto;">
          <h2>Mock Atlan Login</h2>
          <p>This simulates the Atlan login page.</p>
          <p><strong>Client ID:</strong> ${client_id}</p>
          <p><strong>State:</strong> ${state?.substring(0, 8)}...</p>
          <button onclick="authorize()" style="background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; width: 100%;">
            Authorize & Login
          </button>
        </div>
        <script>
          function authorize() {
            window.location.href = '${redirect_uri}?code=mock-auth-code-12345&state=${state}';
          }
        </script>
      </body>
    </html>
  `);
});

// Mock token endpoint
app.post('/auth/mock/token', express.urlencoded({ extended: true }), (req, res) => {
  const { code, code_verifier } = req.body;

  // Simulate token exchange
  if (code === 'mock-auth-code-12345') {
    // Generate mock tokens
    const mockAccessToken = Buffer.from(JSON.stringify({
      header: { alg: 'RS256', typ: 'JWT' },
      payload: {
        sub: 'mock-user-123',
        email: 'test@example.com',
        name: 'Test User',
        exp: Math.floor(Date.now() / 1000) + 3600,
        iat: Math.floor(Date.now() / 1000)
      },
      signature: 'mock-signature'
    })).toString('base64');

    res.json({
      access_token: `mock.${mockAccessToken}.signature`,
      id_token: `mock.${mockAccessToken}.signature`,
      refresh_token: 'mock-refresh-token',
      token_type: 'Bearer',
      expires_in: 3600,
      scope: 'openid profile email'
    });
  } else {
    res.status(400).json({ error: 'invalid_grant' });
  }
});

// Mock API endpoint
app.get('/api/mock/user', (req, res) => {
  const authHeader = req.headers.authorization;

  if (authHeader && authHeader.startsWith('Bearer mock.')) {
    res.json({
      id: 'mock-user-123',
      email: 'test@example.com',
      name: 'Test User',
      username: 'testuser',
      roles: ['admin', 'user']
    });
  } else {
    res.status(401).json({ error: 'Unauthorized' });
  }
});

app.listen(PORT, () => {
  console.log(`Mock OAuth server running at http://localhost:${PORT}`);
  console.log('\nTo use this mock server:');
  console.log('1. Update your .env file:');
  console.log('   OAUTH_AUTH_ENDPOINT=http://localhost:3001/auth/mock/authorize');
  console.log('   OAUTH_TOKEN_ENDPOINT=http://localhost:3001/auth/mock/token');
  console.log('2. Run this server: node mock-server.js');
  console.log('3. Run the main app: docker-compose up');
});