import psycopg2
from flask import current_app, g

def get_db():
    """
    Opens new db connection if none exist for current context
    """
    if 'db' not in g:
        conn_str = current_app.config['DB_URL']
        g.db = psycopg2.connect(conn_str)
    return g.db

def close_db(e=None):
    """
    Close db connection
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    """
    Close db on cleanup
    """
    app.teardown_appcontext(close_db)
