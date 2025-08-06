import os


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://root:{os.getenv('DB_PW')}@localhost/mechanic_db"
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


class ProductionConfig:
    # Handle Render's DATABASE_URL which might use 'postgres://' instead of 'postgresql://'
    database_url = (
        os.environ.get("SQLALCHEMY_DATABASE_URI")
        or os.environ.get("DATABASE_URL")
        or "sqlite:///production.db"  # Fallback for local testing
    )
    # Fix postgres:// scheme to postgresql:// for SQLAlchemy compatibility
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    DEBUG = False
    TESTING = False
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    # Rate limiter storage (suppress warning)
    RATELIMIT_STORAGE_URL = "memory://"
