from flask import Flask
from .extensions import ma, limiter, cache
from .models import db  # Import the SQLAlchemy instance from models
from .blueprints.customers import customers_bp  # Import the customers blueprint
from .blueprints.mechanics import mechanics_bp  # Import the mechanics blueprint
from .blueprints.service_tickets import (
    service_tickets_bp,
)  # Import the service tickets blueprint
from .blueprints.inventory import (
    inventory_items_bp,
)  # Import the inventory items blueprint
from flask_swagger_ui import get_swaggerui_blueprint  # Import swagger ui blueprint

SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
API_URL = "/static/swagger.yaml"  # Our API URL (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Mechanic Shop API"}
)


def create_app(config_name):

    # Load app configuration
    app = Flask(__name__)
        
    if config_name == "TestingConfig":
        app.config.from_object("config.TestingConfig")
    elif config_name == "DevelopmentConfig":
        app.config.from_object("config.DevelopmentConfig")
    else:
        raise ValueError("Invalid config name")

    app.config.from_object(f"config.{config_name}")
    app.config["RATELIMIT_STORAGE_URL"] = "redis://localhost:6379"

    # app.config.from_envvar("FLASK_CONFIG", silent=True)

    # Initialize extensions
    ma.init_app(app)  # Initialize Marshmallow
    db.init_app(app)  # Initialize SQLAlchemy
    limiter.init_app(app)
    cache.init_app(app)  # Initialize Flask-Caching

    # Add a root route
    @app.route("/")
    def index():
        return {
            "message": "Welcome to Mechanic Shop API",
            "version": "1.0.0",
            "documentation": "/api/docs/",
            "endpoints": {
                "customers": "/customers",
                "mechanics": "/mechanics",
                "service_tickets": "/service_tickets",
                "inventory": "/inventory",
            },
        }

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service_tickets")
    app.register_blueprint(inventory_items_bp, url_prefix="/inventory")
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
