from app import app
from lib.user_repository import UserRepository


def test_get_make_request_returns_200(client):
    response = client.get("/make_request/1")
    assert response.status_code == 200


def test_get_make_request_shows_unavailable_dates(client):
    response = client.get("/make_request/2")
    html = response.data.decode()
    assert '<td class="unavailable">28</td>' in html


def test_get_sign_up_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_get_log_in_returns_200(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_get_available_spaces_returns_200(client):
    response = client.get("/spaces")
    assert response.status_code == 200


def test_get_requests_returns_200(client):
    response = client.get("/requests")
    assert response.status_code == 200


def test_get_requests_made_returns_200(client):
    response = client.get("/view_requests")
    assert response.status_code == 200


def test_post_user_creates_user(client, db_connection):
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

def test_seccessful_login_sets_sessions(client, db_connection):
    db_connection.seed(("seeds/ignis_makersbnb.sql"))
    response = client.post("/sessions", data={
        'email': 'alice@example.com',
        'password': 'password123',
    }, follow_redirects=True)
    # assert returns a successful repsonse and redirects to spaces template
    assert response.status_code == 200
    assert b"Available Spaces" in response.data

def test_failed_login_does_not_set_session(client, db_connection):
    db_connection.seed(("seeds/ignis_makersbnb.sql"))
    response = client.post("/sessions", data={
        'email': 'Roma@example.com',
        'password': 'password12!!3',
    }, follow_redirects=True)
    # assert returns a successful repsonse and redirects to spaces template
    assert response.status_code == 200
    assert b"Invalid Email Address or Password" in response.data

