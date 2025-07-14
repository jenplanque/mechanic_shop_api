from pdb import run
from app import create_app
app = create_app("DevelopmentConfig")

if __name__ == "__main__":
    app.run(debug=True)
