import os


class DevelopmentConfig:
    # Safely handle missing DB_PW environment variable
    db_password = os.getenv("DB_PW", "defaultpassword")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://root:{db_password}@localhost/mechanic_db"
    )
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300  # Default cache timeout in seconds
    # Rate limiter storage (suppress warning)
    RATELIMIT_STORAGE_URL = "memory://"


class TestingConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory SQLite for testing
    TESTING = True
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    # Rate limiter storage (suppress warning)
    RATELIMIT_STORAGE_URL = "memory://"


# Helper function to process database URL
def get_database_uri():
    database_url = (
        os.environ.get("SQLALCHEMY_DATABASE_URI")
        or os.environ.get("DATABASE_URL")
        or "sqlite:///production.db"  # Fallback for local testing
    )
    # Fix postgres:// scheme to postgresql+pg8000:// for SQLAlchemy compatibility with pg8000
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
    elif database_url and database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)

    return database_url


class ProductionConfig:
    DEBUG = False
    TESTING = False
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    # Rate limiter storage (suppress warning)
    RATELIMIT_STORAGE_URL = "memory://"

    # Defer database URI resolution until it's actually needed
    @staticmethod
    def init_app(app):
        # This method can be called to do additional setup if needed
        pass

    # Use a property or set this in __init__ of the app
    SQLALCHEMY_DATABASE_URI = None  # Will be set dynamically
