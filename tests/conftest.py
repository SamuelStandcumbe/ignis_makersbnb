import pytest
from database_connection import DatabaseConnection
from app import app


@pytest.fixture
def db_connection():
    connection = DatabaseConnection(test_mode=True)
    connection.connect()
    return connection


@pytest.fixture
def client(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")

    app.config["TESTING"] = True

    yield app.test_client()

    app.config["TESTING"] = False