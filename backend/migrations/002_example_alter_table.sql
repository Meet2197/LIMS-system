-- 002_example_alter_table.sql
-- Example of renaming a column in SQLite by recreating the table.
-- Use this pattern for structural changes not supported by simple ALTER TABLE.

BEGIN TRANSACTION;

-- 1) create a new table with the desired structure
CREATE TABLE IF NOT EXISTS users_new (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE,
  password TEXT,
  fullname TEXT,
  affiliation TEXT,
  email TEXT, -- newly added column
  note TEXT
);

-- 2) copy data from old table to new table (set default for new column if desired)
INSERT INTO users_new (id, username, password, fullname, affiliation, note)
SELECT id, username, password, fullname, affiliation, note FROM users;

-- 3) drop old table
DROP TABLE users;

-- 4) rename new table to original name
ALTER TABLE users_new RENAME TO users;

COMMIT;
