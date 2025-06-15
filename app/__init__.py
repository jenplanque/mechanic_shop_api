from flask import Flask
from .extensions import ma, limiter, cache
from .models import db  # Import the SQLAlchemy instance from models
from .blueprints.customers import customers_bp  # Import the customers blueprint
from .blueprints.mechanics import mechanics_bp  # Import the mechanics blueprint
from .blueprints.service_tickets import (
    service_tickets_bp,
)  # Import the service tickets blueprint


def create_app(config_name):
    app = Flask(__name__)

    # Load app configuration
    app.config.from_object(f"config.{config_name}")
    app.config["RATELIMIT_STORAGE_URL"] = "redis://localhost:6379"
    # app.config.from_envvar("FLASK_CONFIG", silent=True)

    # Initialize extensions
    ma.init_app(app)  # Initialize Marshmallow
    db.init_app(app)  # Initialize SQLAlchemy
    limiter.init_app(app)
    cache.init_app(app)  # Initialize Flask-Caching

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service_tickets")

    return app
