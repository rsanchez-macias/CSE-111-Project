from flaskr.library import getUniversity
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from sqlite3 import Error

from flaskr.auth import login_required
from flaskr.db import get_db

from . import library


bp = Blueprint('profile', __name__, url_prefix='/profile/')

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

@bp.route('/', methods=('GET', 'POST'))
def account():

    checked_books = getCheckedBooksForUser(g.user["u_userid"])
    print(checked_books)

    account_info = [g.user['u_name'], g.user['u_email'], getUniversity()[1]]

    return render_template('users/useraccount.html', account_info=account_info, checked_books=checked_books)