-- seed_data.sql: creates a user with a hashed password placeholder.
-- NOTE: hashing is done in app.py at runtime for the default admin. This file demonstrates inserts.
INSERT INTO users (username, password, fullname, affiliation, note)
VALUES ('testuser', 'password-hash-placeholder', 'Test User', 'Lab A', 'Inserted by seed script');
