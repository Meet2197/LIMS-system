-- 001_create_tables.sql
-- Creates core LIMS tables

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL,
  password TEXT NOT NULL,
  fullname TEXT,
  affiliation TEXT,
  note TEXT
);

CREATE TABLE IF NOT EXISTS materials (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  matid TEXT,
  interusername TEXT,
  name TEXT,
  species TEXT,
  note TEXT
);

CREATE TABLE IF NOT EXISTS gels (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  gelid TEXT,
  gelname TEXT,
  geltype TEXT,
  note TEXT
);

CREATE TABLE IF NOT EXISTS plates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  plateid TEXT,
  platename TEXT,
  platenumber TEXT
);

CREATE TABLE IF NOT EXISTS analysis (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  analid TEXT,
  anatype TEXT,
  note TEXT
);

CREATE TABLE IF NOT EXISTS methods (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  metid TEXT,
  methname TEXT,
  note TEXT
);

CREATE TABLE IF NOT EXISTS proteomes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mapid TEXT,
  species TEXT,
  note TEXT

  CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
);
);
