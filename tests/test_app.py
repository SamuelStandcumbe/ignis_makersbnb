def test_get_make_request_returns_200(client):
    response = client.get("/make_request/1")
    assert response.status_code == 200

def test_get_make_request_shows_unavailable_dates(client):
    response = client.get("/make_request/2")
    html = response.data.decode()
    assert '<td class="unavailable">28</td>' in html
