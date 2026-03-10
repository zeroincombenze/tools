from models import init_db
from app import create_app

if __name__ == "__main__":
    init_db("sqlite:///data/database.db")

    create_app().run(debug=True)
