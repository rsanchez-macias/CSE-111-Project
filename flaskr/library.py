from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from random import randint

bp = Blueprint('library', __name__)

def getUser():
    db = get_db()
    user = 'student'
    if db.execute('SELECT l_userid FROM Librarian WHERE l_userid = ?', (g.user["u_userid"],)).fetchone() is not None:
        user = 'librarian'
    return user

def getUniversity():
    db = get_db()
    return db.execute('SELECT * FROM University WHERE un_id = ?',(g.user["u_universityid"],)).fetchone()

def getAllBooks():
    db = get_db()
    return db.execute(
    'SELECT * FROM Books, Author, Stockroom, University WHERE s_universityid = un_id AND b_isbn = s_isbn AND b_authorid = a_authorid AND s_universityid = ?',(g.user["u_universityid"],)
    ).fetchall()
    
def getFilteredBooks(filter, input):

    trimmed_input = input.strip()
    db = get_db()
    input = "%" + trimmed_input + "%"
    if filter == "title":
        temp = 'b_title LIKE "%{}%"'.format(trimmed_input)
    elif filter == 'author':
        temp = 'a_authorname LIKE "%{}%"'.format(trimmed_input)
    elif filter == 'year':
        temp = 'b_publishedyear LIKE ?'
    else:
        temp = "b_isbn = ?"

    query = "SELECT * FROM Books, Author, Stockroom, University WHERE s_universityid = un_id AND b_isbn = s_isbn AND b_authorid = a_authorid AND s_universityid = ? AND " + temp

    books = []
    if filter == 'year' or filter == 'b_isbn':
        books = db.execute(query,([g.user["u_universityid"], trimmed_input])).fetchall()
    else:
        books = db.execute(query,[g.user["u_universityid"]]).fetchall()
    
    return books


def getLibraryUsers():
    db = get_db()
    return db.execute('SELECT * FROM User, University WHERE u_universityid = un_id AND un_id = ?',(g.user["u_universityid"],)).fetchall()

def getFilteredUsers(filter, input):
    db = get_db()
    input = "%" + input + "%"
    if filter == "name":
        temp = 'u_name LIKE ?'
    else:
        temp = 'u_email LIKE ?'
    
    query = "SELECT * FROM User, University WHERE u_universityid = un_id AND un_id = ? AND " + temp

    return db.execute(query,([g.user["u_universityid"], input])).fetchall()
def insertBooks(title, author, year, isbn, copies):
    db = get_db()

    cur = db.cursor()
    checkAuthor = cur.execute('SELECT a_authorid FROM Author WHERE a_authorname = ?', (author,)).fetchone()

    bookId = randint(0,100000)
    while cur.execute('SELECT * FROM Books WHERE b_bookid = ?', (bookId,)).fetchone() is not None:
        bookId = randint(0,100000)
    
    authorId = randint(0,100000)
    while cur.execute('SELECT * FROM Author WHERE a_authorid = ?', (authorId,)).fetchone() is not None:
        authorId = randint(0,100000)

    if checkAuthor is not None:
        db.execute('INSERT INTO Books VALUES (?, ?, ?, ?, ?)',(bookId,isbn,checkAuthor["a_authorid"],year,title))
    else:
        db.execute('INSERT INTO Author VALUES (?, ?)', (authorId,author))
        db.execute('INSERT INTO Books VALUES (?, ?, ?, ?, ?)',(bookId,isbn,authorId,year,title))
        
    db.execute('INSERT INTO StockRoom VALUES (?,?,?)',(g.user["u_universityid"], isbn, copies))   

    db.commit()

def updateBook(isbn, filter, input):
    db = get_db()

    if filter == "title":
        temp = 'b_title = ?'
    elif filter == 'year':
        temp = 'b_publishedyear = ?'
    else:
        temp = "b_isbn = ?"

    query = "UPDATE Books SET " + temp + " WHERE b_isbn = ?"

    db.execute(query,([input, isbn]))

    db.commit()

def deleteBook(isbn):
    db = get_db()
    cur = db.cursor()
    err = 'None'

    if cur.execute('SELECT * FROM CheckedBooks WHERE cb_isbn = ?', (isbn,)).fetchone() is not None:
            err = 'Book is currently checked out!'
    if cur.execute('SELECT * FROM ReservedBooks WHERE r_isbn = ?', (isbn,)).fetchone() is not None:
            err = 'Book is currently reserved!'
    if cur.execute('SELECT * FROM Books WHERE b_isbn = ?', (isbn,)).fetchone() is None:
            err = 'Book does not exist!'
    if err != 'None':
        flash(err)
    if err == 'None':
        db.execute('DELETE FROM Books WHERE b_isbn = ?', (isbn,) )
    




@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'GET':
        return render_template('library/index.html', user=getUser(), university=getUniversity(), books=getAllBooks())

    if request.method == 'POST':
        button = request.form["button"]
        if button == "refresh books" or button == "return to books":
            return render_template('library/index.html', user=getUser(), university=getUniversity(), books=getAllBooks())
        if button == "filter books":
            return render_template('library/index.html', user=getUser(), university=getUniversity(), books=getFilteredBooks(request.form["filter"],request.form['input']))
        if button == "insert books":
            insertBooks(request.form['title'],request.form['author'],request.form['year'],request.form['isbn'],request.form['copies'])
            return render_template('library/index.html', user=getUser(), university=getUniversity(), books=getAllBooks())
        if button == "update book":
            updateBook(request.form['isbn'], request.form['filter'], request.form['input'])
            return render_template('library/index.html', user=getUser(), university=getUniversity(), books=getAllBooks())
        if button == "refresh users" or button == "search users":
            return render_template('library/index.html', user=getUser(), university=getUniversity(), libraryUsers=getLibraryUsers())
        if button == "filter users":
            return render_template('library/index.html', user=getUser(), university=getUniversity(), libraryUsers=getFilteredUsers(request.form["filter"],request.form['input']))
        if button == "delete book":
            deleteBook(request.form['input'])
            return render_template('library/index.html', user=getUser(), university=getUniversity(), books=getAllBooks())
            
            