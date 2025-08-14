// server.js - Backend API Server
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;
const SECRET_KEY = 'supersecretkey';

// Middleware
app.use(express.json());

// Connect to SQLite database
const db = new sqlite3.Database(path.join(__dirname, 'database.db'), (err) => {
    if (err) {
        console.error('Error connecting to database:', err.message);
    } else {
        console.log('Connected to the SQLite database.');
        initializeDatabase();
    }
});

// Initialize database tables
const initializeDatabase = () => {
    db.serialize(() => {
        db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            fullname TEXT,
            affiliation TEXT,
            note TEXT
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matid TEXT,
            interusername TEXT,
            name TEXT,
            species TEXT,
            note TEXT
        )`);
        
        db.run(`CREATE TABLE IF NOT EXISTS gels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gelid TEXT,
            gelname TEXT,
            geltype TEXT,
            note TEXT
        )`);
        
        db.run(`CREATE TABLE IF NOT EXISTS plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plateid TEXT,
            platename TEXT,
            platenumber TEXT
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analid TEXT,
            anatype TEXT,
            note TEXT
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metid TEXT,
            methname TEXT,
            note TEXT
        )`);
        
        db.run(`CREATE TABLE IF NOT EXISTS proteomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mapid TEXT,
            species TEXT,
            note TEXT
        )`);

        // Check if a default admin user exists, if not, create one
        db.get(`SELECT COUNT(*) as count FROM users WHERE username = 'admin'`, (err, row) => {
            if (err) {
                console.error("Error checking for admin user:", err.message);
                return;
            }
            if (row.count === 0) {
                const username = 'admin';
                // Hash the password before storing it
                bcrypt.hash('admin', 10, (err, hash) => {
                    if (err) {
                        console.error("Error hashing password:", err.message);
                        return;
                    }
                    db.run(`INSERT INTO users (username, password, fullname, affiliation, note) VALUES (?, ?, ?, ?, ?)`,
                        [username, hash, 'Administrator', 'LIMS Admin', 'Initial admin user'],
                        function(err) {
                            if (err) {
                                console.error("Error creating admin user:", err.message);
                            } else {
                                console.log(`Default admin user '${username}' created with password 'admin'`);
                            }
                        }
                    );
                });
            }
        });
    });
};

// Middleware to protect routes
const auth = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    if (token == null) return res.sendStatus(401);

    jwt.verify(token, SECRET_KEY, (err, user) => {
        if (err) return res.sendStatus(403);
        req.user = user;
        next();
    });
};

// Login Route
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    db.get('SELECT * FROM users WHERE username = ?', [username], async (err, row) => {
        if (err) return res.status(500).json({ msg: err.message });
        if (!row) return res.status(401).json({ msg: 'Invalid credentials' });

        const match = await bcrypt.compare(password, row.password);
        if (!match) return res.status(401).json({ msg: 'Invalid credentials' });

        const token = jwt.sign({ username: row.username }, SECRET_KEY);
        res.json({ token });
    });
});

// CRUD API Routes
app.get('/api/:entity', auth, (req, res) => {
    const { entity } = req.params;
    db.all(`SELECT * FROM ${entity}`, [], (err, rows) => {
        if (err) return res.status(500).json({ msg: err.message });
        res.json(rows);
    });
});

app.get('/api/:entity/:id', auth, (req, res) => {
    const { entity, id } = req.params;
    db.get(`SELECT * FROM ${entity} WHERE id = ?`, [id], (err, row) => {
        if (err) return res.status(500).json({ msg: err.message });
        if (!row) return res.status(404).json({ msg: 'Not found' });
        res.json(row);
    });
});

app.post('/api/:entity', auth, (req, res) => {
    const { entity } = req.params;
    const columns = Object.keys(req.body).join(', ');
    const placeholders = Object.keys(req.body).map(() => '?').join(', ');
    const values = Object.values(req.body);

    // If it's a user, hash the password
    if (entity === 'users' && req.body.password) {
        bcrypt.hash(req.body.password, 10, (err, hash) => {
            if (err) return res.status(500).json({ msg: err.message });
            const userValues = [...values];
            userValues[values.findIndex(v => v === req.body.password)] = hash;

            db.run(`INSERT INTO ${entity} (${columns}) VALUES (${placeholders})`, userValues, function(err) {
                if (err) return res.status(500).json({ msg: err.message });
                res.json({ id: this.lastID });
            });
        });
    } else {
        db.run(`INSERT INTO ${entity} (${columns}) VALUES (${placeholders})`, values, function(err) {
            if (err) return res.status(500).json({ msg: err.message });
            res.json({ id: this.lastID });
        });
    }
});

app.put('/api/:entity/:id', auth, (req, res) => {
    const { entity, id } = req.params;
    const updateData = req.body;
    let setClause = Object.keys(updateData).map(key => `${key} = ?`).join(', ');
    let values = Object.values(updateData);

    // If a password is being updated, hash it
    if (entity === 'users' && updateData.password) {
        bcrypt.hash(updateData.password, 10, (err, hash) => {
            if (err) return res.status(500).json({ msg: err.message });
            const passwordIndex = Object.keys(updateData).findIndex(key => key === 'password');
            values[passwordIndex] = hash;
            values.push(id); // add id to the end of the values array for the WHERE clause
            db.run(`UPDATE ${entity} SET ${setClause} WHERE id = ?`, values, function(err) {
                if (err) return res.status(500).json({ msg: err.message });
                res.json({ changes: this.changes });
            });
        });
    } else {
        values.push(id); // add id to the end of the values array for the WHERE clause
        db.run(`UPDATE ${entity} SET ${setClause} WHERE id = ?`, values, function(err) {
            if (err) return res.status(500).json({ msg: err.message });
            res.json({ changes: this.changes });
        });
    }
});

app.delete('/api/:entity/:id', auth, (req, res) => {
    const { entity, id } = req.params;
    db.run(`DELETE FROM ${entity} WHERE id = ?`, id, function(err) {
        if (err) return res.status(500).json({ msg: err.message });
        res.json({ changes: this.changes });
    });
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
