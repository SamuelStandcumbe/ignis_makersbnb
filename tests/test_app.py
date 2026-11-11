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
    response = client.get("/requests/1")
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