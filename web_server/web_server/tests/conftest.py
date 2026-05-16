import pytest
from app import create_app
from models import Base
from sqlalchemy import create_engine

class TestConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

@pytest.fixture
def app():
    # Create Flask app (this initializes DB)
    app = create_app(TestConfig)
    app.config["TESTING"] = True

    # Get the engine created by init_db
    engine = Base.metadata.bind
    if engine is None:
        # fallback (defensive, but usually not needed)
        engine = create_engine(TestConfig.SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(bind=engine)

    yield app

    # Clean up database after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(app):
    return app.test_client()
