-- File containing the schemas of the database

-- DROP TABLE IF EXISTS User;

-- CREATE TABLE User (
--   u_userid INTEGER PRIMARY KEY AUTOINCREMENT,
--   u_name TEXT NOT NULL,
--   u_email TEXT NOT NULL,
--   u_password TEXT NOT NULL
-- );


select *
from StockRoom, Books
where s_isbn = b_isbn and 
    s_universityid = 1
order by b_title;