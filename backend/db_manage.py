"""
Simple DB management script for SQLite migrations and table modifications.

Usage examples:
    python backend/db_manage.py create_all
    python backend/db_manage.py drop_all
    python backend/db_manage.py run_sql backend/migrations/001_create_tables.sql
    python backend/db_manage.py seed backend/seed_data.sql
    python backend/db_manage.py alter_table_add_column <table> <column_def>

Note: SQLite has limited ALTER TABLE support. The helper "alter_table_add_column"
uses "ALTER TABLE ... ADD COLUMN" (works for adding a column). For complex schema
changes (rename/remove column), use the provided example migration that uses a
temporary table rebuild method (see 002_example_alter_table.sql).
"""
import sys
import os
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'backend', 'data')
DB_PATH = os.path.join(DATA_DIR, 'lims.db')
MIGRATIONS_DIR = os.path.join(PROJECT_ROOT, 'backend', 'migrations')

os.makedirs(DATA_DIR, exist_ok=True)

def get_conn():
    return sqlite3.connect(DB_PATH)

def run_sql_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        sql = f.read()
    stmts = [s.strip() for s in sql.split(';') if s.strip()]
    conn = get_conn()
    cur = conn.cursor()
    for s in stmts:
        cur.execute(s)
    conn.commit()
    conn.close()
    print(f'Executed SQL file: {path}')

def create_all():
    path = os.path.join(MIGRATIONS_DIR, '001_create_tables.sql')
    if os.path.exists(path):
        run_sql_file(path)
        print('Created tables from migration.')
    else:
        print('Migration file not found: 001_create_tables.sql')

def drop_all():
    path = os.path.join(MIGRATIONS_DIR, '003_drop_tables.sql')
    if os.path.exists(path):
        run_sql_file(path)
        print('Dropped tables per migration.')
    else:
        print('Migration file not found: 003_drop_tables.sql')

def seed(path):
    if os.path.exists(path):
        run_sql_file(path)
    else:
        print('Seed file not found:', path)

def alter_table_add_column(table, column_def):
    # safe simple ALTER
    conn = get_conn()
    cur = conn.cursor()
    sql = f'ALTER TABLE {table} ADD COLUMN {column_def}'
    cur.execute(sql)
    conn.commit()
    conn.close()
    print('Added column using ALTER TABLE:', sql)

def usage():
    print(__doc__)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'create_all':
        create_all()
    elif cmd == 'drop_all':
        drop_all()
    elif cmd == 'run_sql':
        if len(sys.argv) < 3:
            print('run_sql requires a file path')
        else:
            run_sql_file(sys.argv[2])
    elif cmd == 'seed':
        if len(sys.argv) < 3:
            print('seed requires a file path')
        else:
            seed(sys.argv[2])
    elif cmd == 'alter_table_add_column':
        if len(sys.argv) < 4:
            print('Usage: alter_table_add_column <table> "<column_def>"')
        else:
            alter_table_add_column(sys.argv[2], sys.argv[3])
    else:
        usage()
