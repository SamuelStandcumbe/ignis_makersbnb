from app import app
from lib.user_repository import UserRepository

def test_show_calendar_returns_200():
    client = app.test_client()
    response = client.get("/make_booking")
    assert response.status_code == 200

def test_get_sign_up_returns_200():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200

def test_get_log_in_returns_200():
    client = app.test_client()
    response = client.get("/login")
    assert response.status_code == 200

def test_get_available_spaces_returns_200():
    client = app.test_client()
    response = client.get("/spaces")
    assert response.status_code == 200


def test_get_requests_returns_200():
    client = app.test_client()
    response = client.get("/requests")
    assert response.status_code == 200

def test_get_requests_made_returns_200():
    client = app.test_client()
    response = client.get("/view_requests")
    assert response.status_code == 200

# test post users creates user
def test_post_user_creates_user(db_connection):
    app.config["TESTING"] = True
    db_connection.seed("seeds/ignis_makersbnb.sql")
    client = app.test_client()
    response = client.post("/users", data={
        "username": "carol",
        "email": "carol@gmail.com",
        "password": "Password234",
        "password_confirmation": "Password234",
        "is_host": "on",
    })
    assert response.status_code == 302
    users = UserRepository(db_connection).all()
    assert users[-1].username == "carol"
    assert users[-1].host == True
