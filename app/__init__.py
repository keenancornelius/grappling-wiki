"""
GrapplingWiki - The Free Encyclopedia of Jiu-Jitsu & Grappling
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.wiki import wiki_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(wiki_bp, url_prefix='/wiki')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register template filters
    from app.utils.filters import register_filters
    register_filters(app)

    # Register error handlers
    from app.routes.errors import register_error_handlers
    register_error_handlers(app)

    # Create tables
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app
