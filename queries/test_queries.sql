
SELECT * 
FROM Books, Author, Stockroom, University
WHERE s_universityid = un_id AND 
    b_isbn = s_isbn AND 
    b_authorid = a_authorid AND
    s_universityid = 1 AND
    a_authorname like '%o%';


select *
from Author
order by a_authorname;

SELECT COUNT(*)
FROM CheckedBooks
WHERE cb_isbn = "60929871" AND 
    cb_userid = 1;


SELECT *
FROM CheckedBooks, Books, Author
WHERE cb_isbn = b_isbn AND 
    b_authorid = a_authorid AND
    cb_userid = 2;

DELETE FROM CheckedBooks
WHERE cb_isbn = "1234" AND 
    cb_userid = "1";
