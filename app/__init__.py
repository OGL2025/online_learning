from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Initialize extensions globally
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login' 
login.login_message = 'Please log in to access this page.'
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions with app
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from app.routes.auth import auth as auth_bp
    from app.routes.main import main as main_bp
    from app.routes.instructor import instructor as instructor_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(instructor_bp, url_prefix='/instructor')

    # Create database tables if they don't exist (for dev)
    # In production, use flask db upgrade
    with app.app_context():
        db.create_all()

    return app

# CRITICAL: Create the app instance so Gunicorn can find it via 'app:app'
app = create_app()