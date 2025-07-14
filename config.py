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
    pass
