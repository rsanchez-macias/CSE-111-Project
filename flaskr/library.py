from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('library', __name__)

# Right now i'm extracting all the users but we could, for example, extract all books associated with said user.

def getUser():
    db = get_db()
    user = 'student'
    if db.execute('SELECT l_userid FROM Librarian WHERE l_userid = ?', (g.user["u_userid"],)).fetchone() is not None:
        user = 'librarian'
    return user

def getUniversity():
    db = get_db()
    return db.execute('SELECT * FROM University WHERE un_id = ?',(g.user["u_universityid"],)).fetchone()

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'GET':
        db = get_db()
        books = db.execute(
           'SELECT * FROM Books, Author, Stockroom, University WHERE s_universityid = un_id AND b_isbn = s_isbn AND b_authorid = a_authorid AND s_universityid = ?',(g.user["u_universityid"],)
        ).fetchall()
        return render_template('library/index.html', user=getUser(), university=getUniversity(), books=books)
    
    if request.method == 'POST':
        db = get_db()
        filter = request.form["filter"]
        search = "%" + request.form['search'] + "%"
        if filter == "title":
            temp = 'b_title LIKE ?'
        elif filter == 'author':
            temp = 'a_authorname LIKE ?'
        elif filter == 'year':
            temp = 'b_publishedyear LIKE ?'
        else:
            temp = "b_isbn LIKE ?"

        query = "SELECT * FROM Books, Author, Stockroom, University WHERE s_universityid = un_id AND b_isbn = s_isbn AND b_authorid = a_authorid AND s_universityid = ? AND " + temp

        books = db.execute(
            query,([g.user["u_universityid"], search])
        ).fetchall()

        return render_template('library/index.html', user=getUser(), university=getUniversity(), books=books)

