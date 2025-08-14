"""
Flask backend for LIMS front-end.
Provides JWT auth and CRUD endpoints backed by SQLite.

This file handles the backend API routes, including the user login and authentication.
The login endpoint checks the provided username and password against the SQLite database.
If a valid admin user doesn't exist, it is created with the default password 'password'.
"""
import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory, abort
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import json

# --- Config ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(PROJECT_ROOT, 'backend', 'data')
DB_PATH = os.path.join(DB_DIR, 'lims.db')
STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'frontend', 'public')

os.makedirs(DB_DIR, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='/')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'change-this-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)
jwt = JWTManager(app)

# --- DB helpers ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            fullname TEXT,
            affiliation TEXT,
            note TEXT
        );
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matid TEXT UNIQUE,
            interusername TEXT,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS gels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gelid TEXT UNIQUE,
            gelname TEXT,
            date_created TEXT
        );
        CREATE TABLE IF NOT EXISTS plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plateid TEXT UNIQUE,
            plate_name TEXT,
            plate_description TEXT
        );
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysisid TEXT UNIQUE,
            analysis_name TEXT,
            analysis_description TEXT
        );
        CREATE TABLE IF NOT EXISTS methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            methodid TEXT UNIQUE,
            method_name TEXT,
            method_description TEXT
        );
        CREATE TABLE IF NOT EXISTS proteomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proteomeid TEXT UNIQUE,
            proteome_name TEXT,
            proteome_description TEXT
        );
    ''')
    conn.commit()
    conn.close()

# --- Login route ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'Username and password are required'}), 400

    print(f"Attempting login for username: {username}") # Added for debugging

    conn = get_db_connection()
    cur = conn.cursor()
    user = cur.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        print(f"Login successful for user: {username}") # Added for debugging
        access_token = create_access_token(identity=user['username'])
        return jsonify(token=access_token)
    else:
        print(f"Login failed for user: {username}") # Added for debugging
        return jsonify({'msg': 'Invalid credentials'}), 401

# --- Registration route ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'Username and password are required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if user already exists
    existing_user = cur.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if existing_user:
        conn.close()
        return jsonify({'msg': 'Username already exists'}), 409

    # Hash the password and insert the new user
    hashed_password = generate_password_hash(password)
    try:
        cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({'msg': 'User registered successfully'}), 201
    except Exception as e:
        conn.close()
        return jsonify({'msg': f'Error registering user: {e}'}), 500

# --- API CRUD routes (truncated for brevity, assumes your existing code) ---
# ...
# For example, a route to get all users
@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, fullname, affiliation, note FROM users').fetchall()
    conn.close()
    return jsonify([dict(row) for row in users])

# --- Serve frontend static & index ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # This route serves static files directly from the 'public' directory
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Default to login.html if a specific file is not found
        return send_from_directory(app.static_folder, 'login.html')

if __name__ == '__main__':
    # Ensure tables exist (run migrations)
    create_tables()
    # For demo: if no users exist, create a default admin user
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) as c FROM users')
    count = cur.fetchone()['c']
    if count == 0:
        pw = generate_password_hash('password')
        try:
            cur.execute('INSERT INTO users (username,password,fullname) VALUES (?,?,?)',
                        ('admin', pw, 'Administrator'))
            conn.commit()
            print("Default 'admin' user created with password 'password'")
        except Exception as e:
            print(f"Error creating default admin: {e}")
    conn.close()

    app.run(host='0.0.0.0', port=5000, debug=True)
