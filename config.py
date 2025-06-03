import os


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://root:{os.getenv('DB_PW')}@localhost/mechanic_db"
    )
    DEBUG = True


class TestingConfig:
    pass


class ProductionConfig:
    pass
