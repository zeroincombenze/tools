import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = (
        os.getenv(
            "DATABASE_URL",
            f"sqlite:///{os.path.join(BASE_DIR, 'data', 'database.db')}"
        )
    )
