import os


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://root:{os.getenv('DB_PW')}@localhost/mechanic_db"
    )
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300  # Default cache timeout in seconds


class TestingConfig:
    pass


class ProductionConfig:
    pass
