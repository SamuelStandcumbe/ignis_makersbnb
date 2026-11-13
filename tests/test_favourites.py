
def test_signed_out_user_redirected_from_favourites(client, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")

    response = client.get("/favourites")
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    post_response = client.post("/spaces/1/favourite")
    assert post_response.status_code == 302
    assert post_response.headers["Location"] == "/login"


def test_adding_favourite_shows_on_favourites_page_and_prevents_duplicates(client, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    client.post("/spaces/1/favourite")
    client.post("/spaces/1/favourite")

    response = client.get("/favourites")
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert html.count("Remove from Favourites") == 1


def test_removing_favourite_takes_it_off_favourites_page(client, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    client.post("/spaces/1/favourite")
    client.post("/spaces/1/unfavourite")

    response = client.get("/favourites")
    html = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "No favourites yet" in html