const express = require('express');
const app = express();

// Serve static files from the 'public' directory
app.use(express.static('public'));

// Add a route to redirect the root URL to login.html
app.get('/', (req, res) => {
    res.redirect('/login.html');
});

app.listen(3000, () => {
    console.log('Frontend running on http://localhost:3000');
});
