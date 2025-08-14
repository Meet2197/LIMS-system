const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const FRONTEND_PORT = 3000;
const BACKEND_PORT = 5000;

// Serve static files from the root directory
app.use(express.static(path.join(__dirname, './')));

// Setup the proxy middleware for all /api requests
app.use(
    '/api',
    createProxyMiddleware({
        target: `http://localhost:${BACKEND_PORT}`,
        changeOrigin: true,
        // The path rewrite is important if your backend doesn't expect the /api prefix.
        // If your backend routes are like /login, you would use pathRewrite: {'^/api': ''}
        // In this case, your server.js uses '/api/...' so we can leave it out.
        // pathRewrite: { '^/api': '' },
    })
);

// Redirect the root URL to the login page
app.get('/', (req, res) => {
    res.redirect('/login.html');
});

app.listen(FRONTEND_PORT, () => {
    console.log(`Frontend running on http://localhost:${FRONTEND_PORT}`);
    console.log(`Proxying /api requests to http://localhost:${BACKEND_PORT}`);
});
