import os
from app import create_app
from app.models import db

app = create_app("ProductionConfig")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
