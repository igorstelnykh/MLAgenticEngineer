from flask import Flask
from config import Config

def create_app(config_class=Config):
    """
    Creates flask app and sets up config from object in config.py
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # health check route to confirm app is running
    @app.route('/health')
    def health_check():
        return "OK", 200
    
    return app