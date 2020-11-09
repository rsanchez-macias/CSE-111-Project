-- File containing the schemas of the database

DROP TABLE IF EXISTS User;

CREATE TABLE User (
  u_userid INTEGER PRIMARY KEY AUTOINCREMENT,
  u_name TEXT NOT NULL,
  u_email TEXT NOT NULL,
  u_password TEXT NOT NULL
);

