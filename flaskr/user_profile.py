from datetime import date
from flaskr.checkout import checked
from flaskr.library import getUniversity
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from sqlite3 import Error

from flaskr.db import get_db

from datetime import date
from datetime import timedelta
from datetime import datetime

bp = Blueprint('profile', __name__, url_prefix='/profile/')


def removeCheckedEntry(_book_isbn):
    db = get_db()

    sql = """
        DELETE FROM CheckedBooks
        WHERE cb_isbn = ? AND 
            cb_userid = ?
    """

    try:
        args = [_book_isbn, g.user['u_userid']]
        db.execute(sql, args)
        db.commit()
    except Error as e:
        db.rollback()
        print(e)


def addOneBook(_book_isbn, _university_id):
    db = get_db()

    sql = """
        UPDATE StockRoom
        SET s_bookcount = (
            SELECT s_bookcount + 1
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



def getCheckedBooksForUser(_user_id):
    db = get_db()
    sql = """
        SELECT *
        FROM CheckedBooks, Books, Author
        WHERE cb_isbn = b_isbn AND 
            b_authorid = a_authorid AND
            cb_userid = ?
    """

    books = []

    try:
        cur = db.cursor()
        books = cur.execute(sql, [_user_id]).fetchall()

    except Error as e:
        print(e)

    return books


def getReservedBooksForUser(_user_id):
    db = get_db()

    sql = """
        SELECT *
        FROM ReservedBooks, Books, Author
        WHERE r_isbn = b_isbn AND 
            b_authorid = a_authorid AND
            r_foruserid = ?
    """

    books = []

    try:
        cur = db.cursor()
        books = cur.execute(sql, [_user_id]).fetchall()

    except Error as e:
        print(e)

    return books


def getDiffereceBetweenDates(_isbn, _user_id):

    db = get_db()

    sql = """
        SELECT *
        FROM CheckedBooks
        WHERE cb_userid = ? AND 
            cb_isbn = ?
    """

    dates = []

    try:
        cur = db.cursor()
        dates = cur.execute(sql, [_user_id, _isbn]).fetchone()

    except Error as e:
        print(e)

    d1 = datetime.strptime(dates[2].strftime("%Y-%m-%d"), "%Y-%m-%d")
    d2 = datetime.strptime(dates[3].strftime("%Y-%m-%d"), "%Y-%m-%d")

    return abs((d2 - d1).days)


def updateReservationDate(_isbn, _user_id):

    db = get_db()

    sql = """
        SELECT *
        FROM CheckedBooks
        WHERE cb_userid = ? AND 
            cb_isbn = ?
    """

    checked = []

    try:
        cur = db.cursor()
        checked = cur.execute(sql, [_user_id, _isbn]).fetchone()

    except Error as e:
        print(e)

    
    original_date = checked[3]
    original_date = datetime.combine(original_date, datetime.min.time())
    expiration_date = original_date + timedelta(days=30)

    expiration_date = expiration_date.strftime('%Y-%m-%d')

    sql = """
        UPDATE CheckedBooks
        SET cb_experiationdate = ?
        WHERE cb_userid = ? AND 
            cb_isbn = ?
    """

    try:
        db.execute(sql, [expiration_date, _user_id, _isbn])
        db.commit()

    except Error as e:
        db.rollback()
        print(e)

    return expiration_date



@bp.route('/return_book', methods=('GET', 'POST'))
def return_book():

    if request.method == "GET":
        isbn = request.args.get('data')
        removeCheckedEntry(isbn)
        addOneBook(isbn, g.user['u_universityid'])

    return 'success'


@bp.route('/renew_book', methods=('GET', 'POST'))
def renew_book():

    if request.method == "GET":
        isbn = request.args.get('data')
        
        diff = getDiffereceBetweenDates(isbn, g.user['u_userid'])
        
        if diff < 60:
            new_date = updateReservationDate(isbn, g.user['u_userid'])
            
            return new_date
        

    return 'failure'


@bp.route('/', methods=('GET', 'POST'))
def account():

    checked_books_raw = getCheckedBooksForUser(g.user["u_userid"])
    reserved_books = getReservedBooksForUser(g.user["u_userid"])

    checked_books = []
    counter = 0
   
    for checked_book in checked_books_raw:
        diff = getDiffereceBetweenDates(checked_book['cb_isbn'], checked_book['cb_userid'])
        checked_books.append({})

        checked_books[counter]['b_image_url'] = checked_book['b_image_url']
        checked_books[counter]['b_title'] = checked_book['b_title']
        checked_books[counter]['b_isbn'] = checked_book['b_isbn']
        checked_books[counter]['a_authorname'] = checked_book['a_authorname']
        checked_books[counter]['cb_checkeddate'] = checked_book['cb_checkeddate']
        checked_books[counter]['cb_experiationdate'] = checked_book['cb_experiationdate']

        if diff >= 60:
            checked_books[counter]['disabled'] = 1
        else:
            checked_books[counter]['disabled'] = 0

        counter += 1
        
    account_info = [g.user['u_name'], g.user['u_email'], getUniversity()[1]]

    return render_template('users/useraccount.html', account_info=account_info, checked_books=checked_books, reserved_books=reserved_books)