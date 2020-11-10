import click
import sqlite3
import sys
import os
import random
from sqlite3 import Error
from flask import current_app, g
from flask.cli import with_appcontext


#Function to initiate application
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

#Function to initiate database
def init_db():
    db = get_db()

    initalizeDatabase()
    # with current_app.open_resource('schema.sql') as f:
    #     db.executescript(f.read().decode('utf8'))

#Function to get database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

#Function to close database
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#Function to connect database
@click.command('init-db')
@with_appcontext
def init_db_command():
    #Clear the existing data and create new table
    sys.path.append('/flaskr/')
    
    init_db()
    click.echo('Initialized the database.')

############################################
########## POPULATE TABLES #################
############################################

def openConnection(_dbFile):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """

    conn = None
    try:
        conn = sqlite3.connect(_dbFile)
    except Error as e:
        print(e)


    return conn

def closeConnection(_conn, _dbFile):

    try:
        _conn.close()
    except Error as e:
        print(e)


def createTables(_conn):

    try:
        sql = """CREATE TABLE Books (
                    b_goodreadsid DECIMAL(13, 0), 
                    b_isbn VARCHAR(13) PRIMARY KEY, 
                    b_authornames VARCHAR(40) NOT NULL, 
                    b_publishedyear DECIMAL(4,0) NOT NULL,
                    b_title VARCHAR(50) NOT NULL)"""
        _conn.execute(sql)

        sql = """CREATE TABLE RawBookTags (
                    bt_goodreadsid DECIMAL(13, 0), 
                    bt_tagid DECIMAL(10, 0),
                    bt_tagcount DECIMAL(10, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE BookTags (
                    bt_goodreadsid DECIMAL(13, 0), 
                    bt_tagid DECIMAL(10, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE RawTags (
                    t_tagid DECIMAL(10, 0) PRIMARY KEY,
                    t_description VARCHAR(30, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE Tags (
                    t_tagid DECIMAL(2, 0) PRIMARY KEY,
                    t_description VARCHAR(30, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE University (
                    un_id DECIMAL(2, 0) PRIMARY KEY,
                    un_name VARCHAR(30, 0),
                    un_address VARCHAR(30, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE StockRoom (
                    s_universityid DECIMAL(2, 0),
                    s_isbn VARCHAR(13),
                    s_bookcount DECIMAL(2, 0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE User (
                    u_userid INTEGER PRIMARY KEY AUTOINCREMENT,
                    u_name TEXT NOT NULL,
                    u_email TEXT NOT NULL,
                    u_password TEXT NOT NULL)"""
        _conn.execute(sql)

        sql = """CREATE TABLE Librarian (
                    l_userid INTEGER PRIMARY KEY,
                    l_salary DECIMAL(4,0))"""
        _conn.execute(sql)

        sql = """CREATE TABLE LibraryUser (
                    lu_userid INTEGER PRIMARY KEY,
                    lu_major TEXT NOT NULL)"""
        _conn.execute(sql)

        sql = """CREATE TABLE CheckedBooks (
                    cb_isbn VARCHAR(13),
                    cb_userid INTEGER,
                    cb_checkeddate DATE,
                    cb_experiationdate DATE)"""
        _conn.execute(sql)

        sql = """CREATE TABLE ReservedBooks (
                    r_isbn VARCHAR(13),
                    r_foruserid INTEGER,
                    r_currentuserid INTEGER,
                    r_reason TEXT)"""
        _conn.execute(sql)

        _conn.commit()
        
    except Error as e:
        _conn.rollback()
        print(e)


def dropTables(_conn):

    try:
        sql = "DROP TABLE IF EXISTS Books"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS RawBookTags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS RawTags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS BookTags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS Tags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS University"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS StockRoom"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS User"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS Librarian"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS LibraryUser"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS CheckedBooks"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS ReservedBooks"
        _conn.execute(sql)


        _conn.commit()
    except Error as e:
        _conn.rollback()
        print(e)


def bulkLoadData():
    try:
        cmd = r"sqlite3 ./instance/data.sqlite < ./book_data/bulk_loading.sql"
        os.system(cmd)
    except Error as e:
        print("Error bulkloading data")

def populateUniversity(_conn):
    try:
        products = [
            (1, "UC Merced", "5200 Lake Rd, Merced, CA 95343"),
            (2, "UC Riverside", "900 University Ave, Riverside, CA 92521"),
            (3, "UC San Diego", "9500 Gilman Dr, La Jolla, CA 92093"),
            (4, "UC Santa Barbara", "Santa Barbara, CA 93106"),
            (5, "UC Davis", "1 Shields Ave, Davis, CA 95616")
        ]

        sql = "INSERT INTO University VALUES(?, ?, ?)"
        _conn.executemany(sql, products)

        _conn.commit()
    except Error as e:
        _conn.rollback()
        print(e)

def populateTags(_conn):
    try:
        products = [
            (1, "nonfiction"),
            (2, "action"),
            (3, "romance"),
            (4, "humor"),
            (5, "comedy"),
            (6, "murder"),
            (7, "mystery"),
            (8, "best-books"),
            (9, "novel"),
            (10, "fantasy")
        ]

        sql = "INSERT INTO Tags VALUES(?, ?)"
        _conn.executemany(sql, products)

        _conn.commit()
    except Error as e:
        _conn.rollback()
        print(e)

def cleanBooksTable(_conn):

    try: 
        sql = """
                delete 
                from Books
                where not length(b_title) > 0 or 
                    not b_title glob '*[A-Za-z]*' or 
                    not length(cast(b_publishedyear as text)) > 0 or
                    not length(b_isbn) > 0
            """
        
        _conn.execute(sql)

        _conn.commit()

    except Error as e: 
        _conn.rollback()
        print(e)

def cleanRawTagsTable(_conn, _genres):

    try: 
        sqlDeleteInvalidRows = """
            delete 
            from RawTags
            where not length(t_description) > 0 or 
                not t_description glob '*[A-Za-z]*'
        """

        sqlUpdateGenres = """
            update RawTags
            set t_description = "{}"
            where t_description like "%{}%"
        """

        sqlRemoveLeftOver = """
            delete
            from RawTags 
            where t_description not in (
                select t_description 
                from RawTags 
                where t_description = "nonfiction" or 
                    t_description = "action" or 
                    t_description = "romance" or 
                    t_description = "humor" or 
                    t_description = "comedy" or
                    t_description = "murder" or  
                    t_description = "mystery" or 
                    t_description = "best-books" or
                    t_description = "novel" or
                    t_description = "fantasy"
            )
        """

        _conn.execute(sqlDeleteInvalidRows)
        _conn.commit()

        for genre in _genres:
            tempSql = sqlUpdateGenres.format(genre, genre)
            _conn.execute(tempSql)

        _conn.commit()

        _conn.execute(sqlRemoveLeftOver)
        _conn.commit()

    except Error as e: 
        _conn.rollback()
        print(e)


def cleanTagsData(_conn):

    genres = [
        "nonfiction",
        "action",
        "romance",
        "humor",
        "comedy",
        "murder",
        "mystery",
        "best-books",
        "novel",
        "fantasy"
    ]

    try: 
        
        cleanBooksTable(_conn)
        cleanRawTagsTable(_conn, genres)

    except Error as e: 
        _conn.rollback()
        print(e)

def populateBookTagsTable(_conn):

    genres = [
        "nonfiction",
        "action",
        "romance",
        "humor",
        "comedy",
        "murder",
        "mystery",
        "best-books",
        "novel",
        "fantasy"
    ]

    try: 
        sqlCopy = """ 
            insert into BookTags
            select bt_goodreadsid, bt_tagid
            from RawBookTags
            where bt_tagid in 
                (
                    select t_tagid
                    from RawTags
                )
            order by bt_goodreadsid
        """

        sqlUpdateTagIDs = """
            update BookTags
            set bt_tagid = ?
            where bt_tagid in 
            (
                select t_tagid
                from RawTags
                where t_description = ?
            )
        """

        sqlRemoveDuplicates = """
            delete from BookTags
            where rowid not in (
                select min(rowid)
                from BookTags 
                group by bt_tagid, bt_goodreadsid
            )
        """

        _conn.execute(sqlCopy)

        _conn.commit()
        
        counter = 1

        for genre in genres:
            args = [counter, genre]
            _conn.execute(sqlUpdateTagIDs, args)
            counter += 1

        _conn.commit()
        
        _conn.execute(sqlRemoveDuplicates)
        _conn.commit()

    except Error as e: 
        _conn.rollback()
        print(e)


def dropExtraTables(_conn):
    try: 
        sql = "DROP TABLE IF EXISTS RawBookTags"
        _conn.execute(sql)

        sql = "DROP TABLE IF EXISTS RawTags"
        _conn.execute(sql)

        _conn.commit()

    except Error as e: 
        _conn.rollback()
        print(e)


def insertStockRoomEntries(_conn, _entries, _u_id):

    try:   
        
        entriesToInsert = []

        for entry in _entries:
            isbn = entry[0]
            randomNum = random.randrange(1, 11)

            newEntry = [_u_id, isbn, randomNum]
            entriesToInsert.append(newEntry)

        sql = "INSERT INTO StockRoom VALUES(?, ?, ?)"
        _conn.executemany(sql, entriesToInsert)
        _conn.commit()

    except Error as e:
        _conn.rollback()
        print(e)


def populateStockRooms(_conn):

    try:
        sql = """
            select b_isbn
            from Books
            where substr(b_authornames, 1, 1) >= ? and
                substr(b_authornames, 1, 1) <= ?
        """
        ranges = [
            ('A', 'D'),
            ('E', 'J'),
            ('K', 'L'),
            ('M', 'R'),
            ('S', 'Z')
        ]

        cur = _conn.cursor()

        for i in range(0, 5):
            args = [ranges[i][0], ranges[i][1]] 
            cur.execute(sql, args)

            temp = cur.fetchall()
            insertStockRoomEntries(_conn, temp, i + 1)


    except Error as e: 
        _conn.rollback()
        print(e)

def populateTables(_conn):

    try: 
        bulkLoadData()

        # Manually populated
        populateUniversity(_conn)
        populateTags(_conn)

        # Remap IDs and remove unnecessary tuples
        cleanTagsData(_conn)

        # Populate new table from raw data
        populateBookTagsTable(_conn)

        # Drop original tables
        dropExtraTables(_conn)

        # Populate stock rooms using available data
        populateStockRooms(_conn)

    except Error as e: 
        print(e)

def initalizeDatabase():
    database = r"./instance/data.sqlite"

    # print(os.getcwd())
    
    # create a database connection
    conn = openConnection(database)
    with conn:
        dropTables(conn)
        createTables(conn)
        populateTables(conn)


    closeConnection(conn, database)