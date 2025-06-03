from flask import Flask
# from app.extensions import ma
from .extensions import ma
from .models import db  # Import the SQLAlchemy instance from models

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    # Initialize extensions
    ma.init_app(app)  # Initialize Marshmallow
    db.init_app(app)  # Initialize SQLAlchemy
    # Register blueprints
    
    
    return app