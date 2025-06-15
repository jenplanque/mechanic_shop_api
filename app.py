from app import create_app
from app.models import db 
# from app.models import Customer, Mechanic, ServiceTicket

app = create_app("DevelopmentConfig")

with app.app_context():
    # db.reflect()  # Reflect existing tables
    # db.drop_all()  # Drop all sql tables if needed
    db.create_all()
    app.run()
    