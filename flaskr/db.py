import click
import sqlite3
import sys
from flask import current_app, g
from flask.cli import with_appcontext

from initializeDB import initalizeDatabase

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