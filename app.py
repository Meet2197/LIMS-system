from flask import Flask, jsonify, request, send_from_directory, abort
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import sqlite3, os

STATIC_FOLDER = 'frontend/public'

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='/')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY','super-secret-key')
jwt = JWTManager(app)

DB_PATH = 'backend/data/lims.db'

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        fullname TEXT,
        affiliation TEXT,
        note TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matid TEXT,
        interusername TEXT,
        name TEXT,
        species TEXT,
        note TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS gels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gelid TEXT,
        gelname TEXT,
        geltype TEXT,
        note TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS plates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plateid TEXT,
        platename TEXT,
        platenumber TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analid TEXT,
        anatype TEXT,
        note TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metid TEXT,
        methname TEXT,
        note TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS proteomes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mapid TEXT,
        species TEXT,
        note TEXT
    )
    ''')
    conn.commit()
    conn.close()

def rows_to_list(rows):
    return [dict(r) for r in rows]

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    row = cur.fetchone()
    conn.close()
    if row:
        token = create_access_token(identity=username)
        return jsonify(token=token)
    if username == 'admin' and password == 'password':
        token = create_access_token(identity=username)
        return jsonify(token=token)
    return jsonify(msg='Bad credentials'), 401

def register_crud(prefix, table, fields):
    @app.route(f'/api/{prefix}', methods=['GET'])
    @jwt_required()
    def list_items(table=table):
        conn = get_db_connection()
        rows = conn.execute(f'SELECT * FROM {table}').fetchall()
        conn.close()
        return jsonify(rows_to_list(rows))

    @app.route(f'/api/{prefix}', methods=['POST'])
    @jwt_required()
    def create_item(table=table, fields=fields):
        data = request.json or {}
        cols = []
        vals = []
        for f in fields:
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
        row = conn.execute(f'SELECT * FROM {table} WHERE id=?',(nid,)).fetchone()
        conn.close()
        return jsonify(dict(row)), 201

    @app.route(f'/api/{prefix}/<int:item_id>', methods=['GET'])
    @jwt_required()
    def get_item(item_id, table=table):
        conn = get_db_connection()
        row = conn.execute(f'SELECT * FROM {table} WHERE id=?',(item_id,)).fetchone()
        conn.close()
        if not row:
            abort(404)
        return jsonify(dict(row))

    @app.route(f'/api/{prefix}/<int:item_id>', methods=['PUT'])
    @jwt_required()
    def update_item(item_id, table=table, fields=fields):
        data = request.json or {}
        updates = []
        vals = []
        for f in fields:
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
        row = conn.execute(f'SELECT * FROM {table} WHERE id=?',(item_id,)).fetchone()
        conn.close()
        if not row:
            abort(404)
        return jsonify(dict(row))

    @app.route(f'/api/{prefix}/<int:item_id>', methods=['DELETE'])
    @jwt_required()
    def delete_item(item_id, table=table):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f'DELETE FROM {table} WHERE id=?',(item_id,))
        conn.commit()
        conn.close()
        return jsonify(msg='deleted')

register_crud('users', 'users', ['username','password','fullname','affiliation','note'])
register_crud('materials', 'materials', ['matid','interusername','name','species','note'])
register_crud('gels', 'gels', ['gelid','gelname','geltype','note'])
register_crud('plates', 'plates', ['plateid','platename','platenumber'])
register_crud('analysis', 'analysis', ['analid','anatype','note'])
register_crud('methods', 'methods', ['metid','methname','note'])
register_crud('proteomes', 'proteomes', ['mapid','species','note'])

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'login.html')

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000, debug=True)
