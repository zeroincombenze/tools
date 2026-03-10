import pytest
from app import create_app
from models import Base, engine


@pytest.fixture(scope="session")
def app():
    # Create tables
    Base.metadata.create_all(bind=engine)

    app = create_app()
    app.config["TESTING"] = True

    yield app

    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(app):
    return app.test_client()
