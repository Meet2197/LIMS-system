Backend for LIMS front-end
==========================

How to run (local development)
------------------------------
1. create a venv (optional but recommended)
   python -m venv venv
   source venv/bin/activate

2. install requirements:
   pip install -r requirements.txt

3. start app:
   python backend/app.py

   The server will create the SQLite database at backend/data/lims.db if missing,
   run the 001 migration to create tables, and create a default admin user
   with username `admin` and password `password` if the users table is empty.

Database management
-------------------
Use the db_manage.py helper to run migrations or alter tables:

# run create migrations
python backend/db_manage.py create_all

# drop tables
python backend/db_manage.py drop_all

# run arbitrary SQL migration file
python backend/db_manage.py run_sql backend/migrations/002_example_alter_table.sql

# add a simple column to a table
python backend/db_manage.py alter_table_add_column users "email TEXT"

Security notes
--------------
- For production, change JWT_SECRET_KEY and remove the default admin fallback.
- Passwords are stored hashed by default when created from the default-admin creation inside app.py (uses werkzeug generate_password_hash).
- If you add users via the API, POST to /api/users must include a hashed password if you wish to store the hash manually; better: extend the API to accept plaintext and server-side hash (I can add that if you want).
