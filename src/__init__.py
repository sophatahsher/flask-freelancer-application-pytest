import logging
import os
from logging.handlers import RotatingFileHandler

import sqlalchemy as sqla
from click import echo

from flask import Flask
from flask.logging import default_handler
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect


db = SQLAlchemy()
csrf_protection = CSRFProtect()
login = LoginManager()
login.login_view = "freelancers.login"

# -----------------------------------
# Create Application Factory Function
# -----------------------------------

def create_app():
    # Create the Flask application
    app = Flask(__name__)

    # Configure the Flask application
    config_type = os.getenv('CONFIG_TYPE', default='config.config.DevelopmentConfig')
    app.config.from_object(config_type)

    initialize_extensions(app)
    register_blueprints(app)
    configure_logging(app)
    register_cli_commands(app)

    # Check if the database needs to be initialized
    engine = sqla.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    inspector = sqla.inspect(engine)
    if not inspector.has_table("users"):
        with app.app_context():
            db.drop_all()
            db.create_all()
            app.logger.info('Initialized the database!')
    else:
        app.logger.info('Database already contains the users table.')

    return app

# ----------------
# Helper Functions
# ----------------

def initialize_extensions(app):
    # Since the application instance is now created, pass it to each Flask
    # extension instance to bind it to the Flask application instance (app)
    db.init_app(app)
    #csrf_protection.init_app(app)
    login.init_app(app)

    # Flask-Login configuration
    from src.models import Freelancer

    @login.user_loader
    def load_user(user_id):
        return Freelancer.query.filter(Freelancer.id == int(user_id)).first()


def register_blueprints(app):
    # Since the application instance is now created, register each Blueprint
    # with the Flask application instance (app)
    from src.packages import packages_blueprint
    from src.freelancers import freelancers_blueprint

    app.register_blueprint(packages_blueprint)
    app.register_blueprint(freelancers_blueprint)


def configure_logging(app):
    # Logging Configuration
    if app.config['LOG_WITH_GUNICORN']:
        gunicorn_error_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers.extend(gunicorn_error_logger.handlers)
        app.logger.setLevel(logging.DEBUG)
    else:
        file_handler = RotatingFileHandler('instance/flask-freelancer-management.log',
                                           maxBytes=16384,
                                           backupCount=20)
        file_formatter = logging.Formatter('%(asctime)s %(levelname)s %(threadName)s-%(thread)d: %(message)s [in %(filename)s:%(lineno)d]')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    # Remove the default logger configured by Flask
    app.logger.removeHandler(default_handler)

    app.logger.info('Starting the Flask User Management App...')


def register_cli_commands(app):
    @app.cli.command('init_db')
    def initialize_database():
        """Initialize the database."""
        db.drop_all()
        db.create_all()
        echo('Initialized the database!')


