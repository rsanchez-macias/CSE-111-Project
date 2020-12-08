from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from sqlite3 import Error

from flaskr.auth import login_required
from flaskr.db import get_db

import datetime

bp = Blueprint('checkout', __name__, url_prefix='/book/')

book_isbn = ""
book_author = ""
book_year = ""
book_title = ""

def removeOneBook(_book_isbn, _university_id):

    db = get_db()

    sql = """
        UPDATE StockRoom
        SET s_bookcount = (
            SELECT s_bookcount - 1
            FROM StockRoom, Books, University
            WHERE b_isbn = s_isbn AND 
                s_universityid = un_id AND 
                s_universityid = ? AND 
                s_isbn = ?)
        WHERE s_isbn = ? AND 
            s_universityid = ?
    """

    args = [_university_id, _book_isbn, _book_isbn, _university_id]

    try:
        db.execute(sql, args)
        db.commit()
    except Error as e:

        db.rollback()
        print(e)



def bookCheckedBefore(_book_isbn, _user_id):

    db = get_db()
    sql = """
        SELECT COUNT(*)
        FROM CheckedBooks
        WHERE cb_isbn = ? AND 
            cb_userid = ?
    """

    args = [_book_isbn, _user_id]
    count = 0

    try:
        cur = db.cursor()

        count = cur.execute(sql, args).fetchone()
        db.commit()
    except Error as e:
        db.rollback()
        print(e)

    return count[0]


def bookReservedBefore(_book_isbn, _user_id):

    db = get_db()
    sql = """
        SELECT COUNT(*)
        FROM ReservedBooks
        WHERE r_isbn = ? AND 
            r_foruserid = ?
    """

    args = [_book_isbn, _user_id]
    count = 0

    try:
        cur = db.cursor()

        count = cur.execute(sql, args).fetchone()
        db.commit()
    except Error as e:
        db.rollback()
        print(e)

    return count[0]


def getReasonForReservation(_university_id):

    db = get_db()
    sql = """
        SELECT COUNT(*)
        FROM StockRoom
        WHERE s_universityid = ?
    """

    reasonOne = "NOT IN SCHOOL"
    reasonTwo = "NO MORE COPIES"

    args = [_university_id]
    count = 0

    try:
        cur = db.cursor()

        count = cur.execute(sql, args).fetchone()
        db.commit()
    except Error as e:
        db.rollback()
        print(e)

    if count:
        return reasonTwo
    else: 
        return reasonOne



@bp.route('/redirect_checked/', methods=('GET', 'POST'))
def redirect_user():
    choice = request.form["button"]

    if choice == "Go back to book":
        return redirect(url_for('book.description'))
    else:
        return redirect(url_for('library.index'))


def insertCheckedEntry(_entry):
    db = get_db()
    try:
        sql = "INSERT INTO CheckedBooks VALUES(?, ?, ?, ?)"

        db.execute(sql, _entry)
        db.commit()
    except Error as e:
        db.rollback()
        print(e)

def insertReservedEntry(_entry):
    db = get_db()
    try:
        sql = "INSERT INTO ReservedBooks VALUES(?, ?, ?, ?)"

        db.execute(sql, _entry)
        db.commit()
    except Error as e:
        db.rollback()
        print(e)


@bp.route('/reserved/' , methods=('GET', 'POST'))
def reserved():
    success = "The book has been successfully reserved!"
    failure = "Sorry, you already reserved this book before"

    count = bookReservedBefore(book_isbn, g.user['u_userid'])

    message = ""


    # make reservation
    if count == 0:
        reservationDate = datetime.datetime.today()
        reservationDate = reservationDate.strftime('%Y-%m-%d')


        reason = getReasonForReservation(g.user['u_universityid'])

        newEntry = [
            book_isbn,
            g.user['u_userid'],
            reservationDate,
            reason
        ]

        insertReservedEntry(newEntry)

        message = success
    else:
        message = failure
    
    image_url = getBookImage(book_isbn)

    return render_template('users/checkout.html', image_url=image_url[0], info_msg=message)



@bp.route('/checked/', methods=('GET', 'POST'))
def checked():

    success = "The book has been successfully checked out!"
    failure = "Sorry, you already checkedout this book"

    count = bookCheckedBefore(book_isbn, g.user['u_userid'])
    message = ""

    if count == 0:
        removeOneBook(book_isbn, g.user['u_universityid'])
        
        checkedDate = datetime.datetime.today()
        expirationDate = checkedDate + datetime.timedelta(days=30)

        checkedDate = checkedDate.strftime('%Y-%m-%d')
        expirationDate = expirationDate.strftime('%Y-%m-%d')
        newEntry = [
            book_isbn,
            g.user['u_userid'],
            checkedDate,
            expirationDate
        ]

        insertCheckedEntry(newEntry)

        message = success
    else:
        message = failure
    
    image_url = getBookImage(book_isbn)

    return render_template('users/checkout.html', image_url=image_url[0], info_msg=message)


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

    if count is None:
        return 0
    else: 
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
