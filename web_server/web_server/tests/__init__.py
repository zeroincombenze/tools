import pytest
from app import create_app
from models import init_db, Base

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def app():
    # initialize a fresh in-memory database
    init_db(TEST_DATABASE_URL)

    app = create_app()
    app.config["TESTING"] = True

    yield app

    # cleanup (not strictly required for :memory:)
    Base.metadata.drop_all(bind=Base.metadata.bind)


@pytest.fixture
def client(app):
    return app.test_client()
