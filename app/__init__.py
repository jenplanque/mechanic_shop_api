from flask import Flask
# from app.extensions import ma
from .extensions import ma
from .models import db  # Import the SQLAlchemy instance from models
from .blueprints.customers import customers_bp  # Import the customers blueprint

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    # Initialize extensions
    ma.init_app(app)  # Initialize Marshmallow
    db.init_app(app)  # Initialize SQLAlchemy
    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    
    return app