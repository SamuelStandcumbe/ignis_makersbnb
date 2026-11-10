import pytest
from database_connection import DatabaseConnection

@pytest.fixture
def db_connection():
    connection = DatabaseConnection(test_mode=True)
    connection.connect()
    return connection