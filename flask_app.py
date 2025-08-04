import os
from app import create_app
from app.models import db

app = create_app("ProductionConfig")
# app = create_app("DevelopmentConfig")
# config_name = os.getenv("FLASK_CONFIG", "DevelopmentConfig")
# app = create_app(config_name)


with app.app_context():
    # db.reflect()  # Reflect existing tables
    # db.drop_all()  # Drop all sql tables if needed
    db.create_all()
    app.run(port=5000, debug=True)
