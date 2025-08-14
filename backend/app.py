"""
Flask backend for LIMS front-end.
Provides JWT auth and CRUD endpoints backed by SQLite.

Place this file at backend/app.py and run:
    pip install -r requirements.txt
    python backend/app.py

It will create the SQLite DB at backend/data/lims.db and run create_tables() on startup.
"""
import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory, abort
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

# Config
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

def rows_to_list(rows):
    return [dict(r) for r in rows]

# --- Create tables if missing on startup ---
def create_tables():
    """Create core tables if they do not exist."""
    sql_path = os.path.join(PROJECT_ROOT, 'backend', 'migrations', '001_create_tables.sql')
    if os.path.exists(sql_path):
        run_sql_file(sql_path)
    else:
        # fallback if migration file missing: create minimal tables
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            fullname TEXT,
            affiliation TEXT,
            note TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matid TEXT, interusername TEXT, name TEXT, species TEXT, note TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS gels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gelid TEXT, gelname TEXT, geltype TEXT, note TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plateid TEXT, platename TEXT, platenumber TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analid TEXT, anatype TEXT, note TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metid TEXT, methname TEXT, note TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS proteomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mapid TEXT, species TEXT, note TEXT
        )""")
        conn.commit()
        conn.close()

def run_sql_file(path):
    """Execute SQL statements in a .sql file (simple splitter on ';')."""
    with open(path, 'r', encoding='utf-8') as f:
        sql = f.read()
    stmts = [s.strip() for s in sql.split(';') if s.strip()]
    conn = get_db_connection()
    cur = conn.cursor()
    for st in stmts:
        cur.execute(st)
    conn.commit()
    conn.close()

# --- Authentication ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify(msg='username and password required'), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username=?', (username,))
    row = cur.fetchone()
    conn.close()

    if row:
        stored_hash = row['password']
        if check_password_hash(stored_hash, password):
            token = create_access_token(identity=username)
            return jsonify(token=token)
        else:
            return jsonify(msg='Bad credentials'), 401
    # fallback default admin for first-time convenience
    if username == 'admin' and password == 'password':
        token = create_access_token(identity=username)
        return jsonify(token=token)
    return jsonify(msg='Bad credentials'), 401


# --- Generic CRUD registration helper ---
def register_crud(prefix, table, allowed_fields):
    """Registers routes: GET /api/<prefix>, POST /api/<prefix>,
       GET/PUT/DELETE /api/<prefix>/<id>"""
    list_route = f'/api/{prefix}'
    item_route = f'/api/{prefix}/<int:item_id>'

    @app.route(list_route, methods=['GET'])
    @jwt_required()
    def list_items(table=table):
        conn = get_db_connection()
        rows = conn.execute(f'SELECT * FROM {table}').fetchall()
        conn.close()
        return jsonify(rows_to_list(rows))

    @app.route(list_route, methods=['POST'])
    @jwt_required()
    def create_item(table=table, allowed_fields=allowed_fields):
        data = request.json or {}
        cols = []
        vals = []
        for f in allowed_fields:
            if f in data:
                cols.append(f)
                vals.append(data[f])
        conn = get_db_connection()
        cur = conn.cursor()
        if cols:
            qcols = ','.join(cols)
            qmarks = ','.join(['?']*len(vals))
            cur.execute(f'INSERT INTO {table} ({qcols}) VALUES ({qmarks})', tuple(vals))
        else:
            cur.execute(f'INSERT INTO {table} DEFAULT VALUES')
        conn.commit()
        nid = cur.lastrowid
        row = conn.execute(f'SELECT * FROM {table} WHERE id=?', (nid,)).fetchone()
        conn.close()
        return jsonify(dict(row)), 201

    @app.route(item_route, methods=['GET'])
    @jwt_required()
    def get_item(item_id, table=table):
        conn = get_db_connection()
        row = conn.execute(f'SELECT * FROM {table} WHERE id=?', (item_id,)).fetchone()
        conn.close()
        if not row:
            abort(404)
        return jsonify(dict(row))

    @app.route(item_route, methods=['PUT'])
    @jwt_required()
    def update_item(item_id, table=table, allowed_fields=allowed_fields):
        data = request.json or {}
        updates = []
        vals = []
        for f in allowed_fields:
            if f in data:
                updates.append(f + '=?')
                vals.append(data[f])
        if not updates:
            return jsonify(msg='No fields to update'), 400
        vals.append(item_id)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f'UPDATE {table} SET ' + ','.join(updates) + ' WHERE id=?', tuple(vals))
        conn.commit()
        row = conn.execute(f'SELECT * FROM {table} WHERE id=?', (item_id,)).fetchone()
        conn.close()
        if not row:
            abort(404)
        return jsonify(dict(row))

    @app.route(item_route, methods=['DELETE'])
    @jwt_required()
    def delete_item(item_id, table=table):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f'DELETE FROM {table} WHERE id=?', (item_id,))
        conn.commit()
        conn.close()
        return jsonify(msg='deleted')

# Register entities (fields must match DB columns)
register_crud('users', 'users', ['username', 'password', 'fullname', 'affiliation', 'note'])
register_crud('materials', 'materials', ['matid', 'interusername', 'name', 'species', 'note'])
register_crud('gels', 'gels', ['gelid', 'gelname', 'geltype', 'note'])
register_crud('plates', 'plates', ['plateid', 'platename', 'platenumber'])
register_crud('analysis', 'analysis', ['analid', 'anatype', 'note'])
register_crud('methods', 'methods', ['metid', 'methname', 'note'])
register_crud('proteomes', 'proteomes', ['mapid', 'species', 'note'])

# Optional: CSV export for an entity
@app.route('/api/<entity>/export', methods=['GET'])
@jwt_required()
def export_entity_csv(entity):
    allowed = {'users','materials','gels','plates','analysis','methods','proteomes'}
    if entity not in allowed:
        abort(404)
    conn = get_db_connection()
    rows = conn.execute(f'SELECT * FROM {entity}').fetchall()
    conn.close()
    # build CSV
    if not rows:
        return jsonify(rows=[])
    cols = rows[0].keys()
    lines = [','.join(cols)]
    for r in rows:
        lines.append(','.join('' if r[c] is None else str(r[c]).replace(',', '') for c in cols))
    return ('\n'.join(lines), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename={entity}.csv'
    })

# Serve frontend static & index
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # default to login.html
        return send_from_directory(app.static_folder, 'login.html')


if __name__ == '__main__':
    # Ensure tables exist (run migrations)
    create_tables()
    # For demo: if no users exist, create a default admin user (safe for local dev)
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
            print('Created default user: admin / password (change it!)')
        except Exception:
            pass
    conn.close()
    # Start app
    app.run(host='0.0.0.0', port=5000, debug=True)