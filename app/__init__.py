from flask import Flask, jsonify
from config import Config
from . import db
import logging
import click

# logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_app(config_class=Config):
    """
    Creates flask app and sets up config from object in config.py
    """
    # create app and add db handler
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    @app.route('/health')
    def health_check():
        """
        Health check route to check app and db connection
        """
        try:
            conn = db.get_db()
            conn.cursor().execute("SELECT 1")
            return "OK", 200
        except Exception as e:
            return "DB connection failed", 500
        
    # register blueprints from routes
    from . import routes
    app.register_blueprint(routes.alerts_bp)

    # generic error handler
    @app.errorhandler(Exception)
    def handle_error(e):
        """
        Generic error handler for any undhanled exceptions
        """
        logging.error(f"Unhandled exception occured: {e}")
        
        return jsonify(error="Internal server error"), 500
    
    # agent trigger command(import here to prevent potential circular dependency)
    from . import stress_detector
    @app.cli.command("run-agent")
    @click.argument("filepath")
    def run_agent_cmd(filepath):
        """
        Command to run agent with filepath as arg
        """
        stress_detector.run_agent(filepath)

    return app
