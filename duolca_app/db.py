import sqlite3

import click
from flask import current_app, g # g is an object unique to each request, stores data 
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect( # Establishes a connection app pointed at in current_app
            current_app.config['DATABASE'], # Points to the app handling the request
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # The connection returns rows that behave like dictionaries'
    return g.db

def close_db(e=None): # Checks that the connection was creating, by checking value of g.db
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db() # Returns a database connection, used to execute commands in from this file

    with current_app.open_resource('schema.sql') as f: # Opens a file relative to duolca package
        db.executescript(f.read().decode('utf8')) 

@click.command('init-db') 
@with_appcontext
def init_db_command():
    # Clear the existing data and create new tables when initializing
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db) # Indicates to Flask that close_db function should be called'
    app.cli.add_command(init_db_command) # Adds a new Flask command'
