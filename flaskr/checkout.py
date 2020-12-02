from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from sqlite3 import Error

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('checkout', __name__, url_prefix='/book/')

book_isbn = ""
book_author = ""
book_year = ""
book_title = ""

@bp.route('/checked/', methods=('GET', 'POST'))
def checked():
    return render_template('users/checkout.html')


@bp.route('/clearfields/', methods=('GET', 'POST'))
def clear():

    print("oh no")
    global book_isbn 
    global book_author 
    global book_year
    global book_title

    book_isbn = ""
    book_author = ""
    book_year = ""
    book_title = ""


def getBookImage(_isbn):
    db = get_db()
    sql = "SELECT b_image_url FROM Books WHERE b_isbn = ?"

    image_url = None

    try: 
        image_url = db.execute(sql, [_isbn]).fetchone()
        db.commit()
    except Error as e:
        db.rollback()
        print(e)

    return image_url

def getAvailableBooks():
    db = get_db()
    
    sql = """
        SELECT 
            CASE 
                WHEN s_bookcount IS NULL THEN 0
                ELSE s_bookcount
            END AS bookcount
        FROM 
            Books

            LEFT JOIN 

            (SELECT * 
            FROM StockRoom 
            WHERE s_universityid = 1) S

            ON S.s_isbn = b_isbn
        WHERE s_universityid = ? AND 
            s_isbn = ?
    """

    user_universityid = g.user["u_universityid"]

    count = 0

    try: 
        args = [user_universityid, book_isbn]
        count = db.execute(sql, args).fetchone()
        db.commit()
    except Error as e:
        db.rollback()
        print(e)

    return count[0]


@bp.route('/description/', methods=('GET', 'POST'))
def loadBook():

    image_url = getBookImage(book_isbn)
    count = getAvailableBooks()
    
    return render_template('users/bookoverview.html', book_title=book_title, book_isbn=book_isbn, 
            book_year=book_year, book_author= book_author, image_url=image_url, book_count=count)


@bp.route('/process/', methods=('GET', 'POST'))
def processClick():

    global book_isbn 
    global book_author 
    global book_year
    global book_title

    book_isbn = request.args.get("isbn")
    book_author = request.args.get("author")
    book_title = request.args.get("title")
    book_year = request.args.get("year")

    return redirect(url_for('book.description'))
