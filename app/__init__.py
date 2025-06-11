from flask import Flask
from config import Config
from . import db

def create_app(config_class=Config):
    """
    Creates flask app and sets up config from object in config.py
    """
    # create app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # init db handling
    db.init_app(app)

    @app.route('/health')
    def health_check():
        """
        health check route to check app and db connection
        """
        try:
            conn = db.get_db()
            conn.cursor().execute("SELECT 1")
            return "OK", 200
        except Exception as e:
            return "DB connection failed", 500
    
    return app