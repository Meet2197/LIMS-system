import sys
import os
import sqlite3

# Path to the SQLite database
db_path = "lims.db"

# Function to execute SQL scripts
def execute_sql_script(script_path):
    with open(script_path, 'r') as file:
        sql_script = file.read()
    with sqlite3.connect(db_path) as conn:
        conn.executescript(sql_script)

# Apply migrations
migrations_dir = "backend/migrations"
for migration_file in sorted(os.listdir(migrations_dir)):
    if migration_file.endswith(".sql"):
        execute_sql_script(os.path.join(migrations_dir, migration_file))

# Seed the database with initial data
seed_file = "seed_data.sql"
if os.path.exists(seed_file):
    execute_sql_script(seed_file)

print("Database setup complete.")