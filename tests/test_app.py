from app import app

def test_get_books_returns_200():
    client = app.test_client()
    response = client.get("/make_booking")
    assert response.status_code == 200