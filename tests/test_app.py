from app import app

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

def test_get_create_space_form_returns_200():
    client = app.test_client()
    response = client.get("/spaces/new")
    assert response.status_code == 200

def test_get_requests_returns_200():
    client = app.test_client()
    response = client.get("/requests")
    assert response.status_code == 200

def test_get_requests_made_returns_200():
    client = app.test_client()
    response = client.get("/view_requests")
    assert response.status_code == 200