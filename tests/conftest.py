import pytest
from database_connection import DatabaseConnection
from app import app


@pytest.fixture
def db_connection():
    conn = DatabaseConnection(test_mode=True)
    conn.connect()
    return conn


@pytest.fixture
def client(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    app.config["DATABASE_CONNECTION"] = db_connection

    yield app.test_client()

    app.config["DATABASE_CONNECTION"] = None