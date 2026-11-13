import os
import sys
import pytest
from xprocess import ProcessStarter
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


@pytest.fixture
def test_web_address(xprocess):
    python_executable = sys.executable
    app_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.py"))
    port = 5002

    class Starter(ProcessStarter):
        env = {**os.environ, "APP_ENV": "test", "PORT": str(port)}
        pattern = "Running on http://"
        timeout = 10
        args = [python_executable, app_file]

    xprocess.ensure("flask_test_server", Starter)

    yield f"http://localhost:{port}"

    xprocess.getinfo("flask_test_server").terminate()