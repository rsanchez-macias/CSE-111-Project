from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from random import randint

from sqlite3 import Error

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
    if filter == 'year' or filter == 'isbn':
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

    users = db.execute(query,([g.user["u_universityid"], input])).fetchall()

    return users


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


    try: 
        default_book_img = "https://dl.acm.org/specs/products/acm/releasedAssets/images/cover-default--book.svg"

        if checkAuthor is not None:
            new_book = (bookId,isbn, checkAuthor["a_authorid"],year,title, default_book_img, default_book_img)
            db.execute('INSERT INTO Books VALUES (?, ?, ?, ?, ?, ?, ?)', new_book)
        else:
            new_book = (bookId, isbn, authorId, year, title, default_book_img, default_book_img)
            db.execute('INSERT INTO Author VALUES (?, ?)', (authorId,author))
            db.execute('INSERT INTO Books VALUES (?, ?, ?, ?, ?, ?, ?)', new_book)
            
        db.execute('INSERT INTO StockRoom VALUES (?,?,?)', (g.user["u_universityid"], isbn, copies))   

        db.commit()
    except Error as e: 
        db.rollback()
        print(e)


def updateBook(isbn, filter, input):
    db = get_db()

    if filter == "title":
        temp = 'b_title = ?'
    elif filter == 'year':
        temp = 'b_publishedyear = ?'
    else:
        temp = "b_isbn = ?"

    try: 

        query = "UPDATE Books SET " + temp + " WHERE b_isbn = ?"
        db.execute(query,([input, isbn]))

        if filter == "isbnNEW":
            temp = "s_isbn = ?"
            query = "UPDATE StockRoom SET " + temp + " WHERE s_isbn = ?"
            db.execute(query, ([input, isbn]))

            temp = "cb_isbn = ?"
            query = "UPDATE CheckedBooks SET " + temp + " WHERE cb_isbn = ?"
            db.execute(query, ([input, isbn]))

            temp = "r_isbn = ?"
            query = "UPDATE ReservedBooks SET " + temp + " WHERE r_isbn = ?"
            db.execute(query, ([input, isbn]))

        db.commit()
    except Error as e: 
        db.rollback()
        print(e)


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
        try: 
            db.execute('DELETE FROM Books WHERE b_isbn = ?', (isbn,) )
            db.execute('DELETE FROM StockRoom WHERE s_isbn = ?', (isbn,) )

            db.commit()

        except Error as e:
            db.rollback()
            print(e)


def getBooksByGenre(_genre):
    db = get_db()

    books = []

    try:
        sql = """
            SELECT *
            FROM Books, Author, Stockroom, University, BookTags, Tags
            WHERE b_bookid = bt_bookid AND 
                bt_tagid = t_tagid AND 
                b_authorid = a_authorid AND 
                s_universityid = un_id AND 
                b_isbn = s_isbn AND
                t_description = ? AND
                s_universityid = ?
        """

        args = [_genre, g.user['u_universityid']]
        cur = db.cursor()

        books = cur.execute(sql, args).fetchall()
    except Error as e:
        print(e)

    return books

def divideIntoSections(_books):
    global books
    global max_section

    multiple = 20
    list_counter = -1

    for i, book in enumerate(_books):

        if i % multiple == 0:
            list_counter += 1
            books.append([]) 

        books[list_counter].append(book)

    max_section = len(books) - 1


section_num = 0
books = []
max_section = 0

@bp.route('/page', methods=('GET', 'POST'))
def navigate():
    global section_num

    if request.method == 'POST':
        button = request.form["button"]

        if button == "next":
            section_num += 1
            return render_template('library/index.html', user=getUser(), university=getUniversity(), 
                books=books[section_num], sec_num=section_num, max_section=max_section, hide=0)
        elif button == "back":
            section_num -= 1
            return render_template('library/index.html', user=getUser(), university=getUniversity(), 
                books=books[section_num], sec_num=section_num, max_section=max_section, hide=0)


@bp.route('/back_to_list', methods=('GET', 'POST'))
def backToList():
    return render_template('library/index.html', user=getUser(), university=getUniversity(), books=books[section_num], 
        sec_num=section_num, max_section=max_section, hide=0)


def handleMainGetRequest():
    global books
    global section_num

    books = []
    section_num = 0

    raw_books = getAllBooks()
    divideIntoSections(raw_books)

    return render_template('library/index.html', user=getUser(), university=getUniversity(), books=books[section_num], 
        sec_num=section_num, max_section=max_section, hide=0)


def handleRefresh():
    global books
    global section_num

    books = []
    section_num = 0

    raw_books = getAllBooks()
    divideIntoSections(raw_books)

    return render_template('library/index.html', user=getUser(), university=getUniversity(), books=books[section_num], 
        sec_num=section_num, max_section=max_section, hide=0)


def handleFilteredBooks():
    global books
    global section_num

    books = []
    section_num = 0

    raw_books = getFilteredBooks(request.form["filter"], request.form['input'])
    divideIntoSections(raw_books)

    to_display_books = []
    if raw_books:
        to_display_books = books[section_num]
    

    return render_template('library/index.html', user=getUser(), university=getUniversity(), books=to_display_books, 
        sec_num=section_num, max_section=max_section, hide=0)


def handleGenreBooks():
    global books
    global section_num

    books = []
    section_num = 0

    genre_chosen = request.form['genre-filter']
    
    raw_books = getBooksByGenre(genre_chosen)
    divideIntoSections(raw_books)

    return render_template('library/index.html', user=getUser(), university=getUniversity(), books=books[section_num], 
        sec_num=section_num, max_section=max_section, hide=0)


def handleDelete():
    deleteBook(request.form['input'])
    return handleRefresh()


@bp.route('/', methods=('GET', 'POST'))
def index():

    if request.method == 'GET':
        return handleMainGetRequest()

    if request.method == 'POST':
        button = request.form["button"]

        if button == "refresh books" or button == "return to books":
            return handleRefresh()

        if button == "filter books":
            search_filter = request.form["filter"]
            if search_filter == 'genre':
                return handleGenreBooks()
            else:
                return handleFilteredBooks()

        if button == "insert books":
            insertBooks(request.form['title'],request.form['author'],request.form['year'],request.form['isbn'],request.form['copies'])
            return handleRefresh()

        if button == "update book":
            updateBook(request.form['isbn'], request.form['filter'], request.form['input'])
            return handleRefresh()

        if button == "refresh users" or button == "search users":
            return render_template('library/index.html', user=getUser(), university=getUniversity(),
                libraryUsers=getLibraryUsers(), hide=1)

        if button == "filter users":
            return render_template('library/index.html', user=getUser(), university=getUniversity(), 
                libraryUsers=getFilteredUsers(request.form["filter"],request.form['input']), hide=1)

        if button == "delete book":
            return handleDelete()
            
            