from flaskr.library import getUniversity
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from sqlite3 import Error

from flaskr.db import get_db


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


@bp.route('/return_book', methods=('GET', 'POST'))
def return_book():

    if request.method == "GET":
        isbn = request.args.get('data')
        removeCheckedEntry(isbn)
        addOneBook(isbn, g.user['u_universityid'])

    return 'success'


@bp.route('/', methods=('GET', 'POST'))
def account():

    checked_books = getCheckedBooksForUser(g.user["u_userid"])

    account_info = [g.user['u_name'], g.user['u_email'], getUniversity()[1]]

    return render_template('users/useraccount.html', account_info=account_info, checked_books=checked_books)