from app import app
from lib.user_repository import UserRepository
from html import unescape
from werkzeug.security import check_password_hash
from playwright.sync_api import Page, expect

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

def test_get_search_results_returns_200(client):
    response = client.get("/search/cottage")
    assert response.status_code == 200

def test_get_log_in_returns_200(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_get_available_spaces_returns_200(client):
    response = client.get("/spaces")
    assert response.status_code == 200


def test_get_requests_returns_302_when_not_logged_in(client):
    response = client.get("/requests")
    assert response.status_code == 302

def test_search_results_shows_relevant_listings(client):
    response = client.get("/search/cottage")
    html = unescape(response.data.decode("utf-8"))

    # Properties of found space name, then description
    assert "cottage" in html
    assert "Compact studio with a double bed" in html

def test_bad_search_results_shows_error(client):
    response = client.get("/search/sss")
    html = unescape(response.data.decode("utf-8"))

    # Properties of found space
    assert "No spaces match your search" in html

def test_search_results_by_location(client):
    response = client.get("/search/london")
    html = unescape(response.data.decode("utf-8"))

    # Properties of found space
    assert 'Brick Lane' in html
    assert "double bed" in html


def test_requests_dashboard_shows_sent_and_received_requests(client, page: Page, test_web_address):
    page.goto(f"{test_web_address}/login")
    page.get_by_placeholder("example@example.com").fill("alice@example.com")
    page.get_by_placeholder("password123").fill("password123")
    page.get_by_role("button", name="Log In").click()
    assert page.url == f"{test_web_address}/spaces"
    page.get_by_role("link", name="Requests").click()
    assert page.url == f"{test_web_address}/requests"
    expect(page.get_by_text("Fisherman's cottage by the harbour"))
    expect(page.get_by_text("Requested dates: 2026-11-28 to 2026-11-30"))

def test_host_can_accept_a_pending_request( db_connection, page:Page, test_web_address):

    # Ensure there is a single request
    db_connection.execute("TRUNCATE TABLE requests;")
    db_connection.execute("INSERT INTO requests (space_id, user_id, approved_status, start_date, end_date, host_id, paid, stripe_session_id) VALUES (1, 2, 'pending', '2026-10-10', '2026-10-12', 1, FALSE, '1212sadad');")

    base_url = test_web_address

    #  Alice logs in and redirects to spaces
    page.goto(f"{base_url}/login")
    page.get_by_placeholder("example@example.com").fill("alice@example.com")
    page.get_by_placeholder("password123").fill("password123")
    page.get_by_role("button", name="Log In").click()
    assert page.url == f"{base_url}/spaces"

    # Click requests page and assert that the button says pending
    page.get_by_role("link", name="Requests").click()
    assert page.url == f"{base_url}/requests"
    first_received_card_before_acceptance = (
        page.locator("section.requests")
        .filter(has=page.get_by_role("heading", name="Requests I've received"))
        .locator("article.card")
        .first
        .all_text_contents()
    )
    assert "Pending" in first_received_card_before_acceptance[0]

    # Press Accept and assert that the status is approved.
    page.get_by_role("button", name="Accept Request").click()
    assert page.url == f"{base_url}/requests"
    first_received_card_after_acceptance = (
            page.locator("section.requests")
            .filter(has=page.get_by_role("heading", name="Requests I've received"))
            .locator("article.card")
            .first
            .all_text_contents()
        )
    assert "Approved" in first_received_card_after_acceptance[0]

def test_host_can_reject_a_pending_request(page:Page, db_connection, test_web_address):

    # Ensure there is a single request
    db_connection.execute('TRUNCATE TABLE requests;')
    db_connection.execute("INSERT INTO requests (space_id, user_id, approved_status, start_date, end_date, host_id, paid, stripe_session_id) VALUES (1, 2, 'pending', '2026-10-10', '2026-10-12', 1, FALSE, '1212sadad');")

    base_url = test_web_address

    #  Alice logs in and redirects to spaces
    page.goto(f"{base_url}/login")
    page.get_by_placeholder("example@example.com").fill("alice@example.com")
    page.get_by_placeholder("password123").fill("password123")
    page.get_by_role("button", name="Log In").click()
    assert page.url == f"{base_url}/spaces"

    # Click requests page and assert that the button says pending
    page.get_by_role("link", name="Requests").click()
    assert page.url == f"{base_url}/requests"
    first_received_card_before_acceptance = (
        page.locator("section.requests")
        .filter(has=page.get_by_role("heading", name="Requests I've received"))
        .locator("article.card")
        .first
        .all_text_contents()
    )
    assert "Pending" in first_received_card_before_acceptance[0]

    # Decline the request and verify it remains visible
    page.get_by_role("button", name="Decline Request").click()
    assert page.url == f"{base_url}/requests"
    received_section = page.locator("section.requests").filter(
        has=page.get_by_role("heading", name="Requests I've received")
    )
    cards = received_section.locator("article.card")
    assert cards.count() == 1
    assert cards.first.locator(".status-declined").inner_text() == "Declined"

    # A resolved request cannot be approved or declined again
    assert cards.first.get_by_role("button", name="Accept Request").count() == 0
    assert cards.first.get_by_role("button", name="Decline Request").count() == 0



def test_post_user_creates_user(client, db_connection):
    response = client.post("/users", data={
        "full_name": "carol",
        "email": "carol@gmail.com",
        "password": "Password234",
        "password_confirmation": "Password234",
        "is_host": "on",
    })

    assert response.status_code == 302

    users = UserRepository(db_connection).all()
    assert users[-1].full_name == "carol"
    assert users[-1].host == True

def test_successful_login_sets_sessions(client, db_connection):
    db_connection.seed(("seeds/ignis_makersbnb.sql"))
    client.post("/users", data={
        "full_name": "Carol",
        "email": "carol@gmail.com",
        "password": "Password234",
        "is_host": "on"
    })
    response = client.post("/sessions", data={
        'email': 'carol@gmail.com',
        'password': 'Password234',
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

def test_successful_logout(client, db_connection):
    db_connection.seed(("seeds/ignis_makersbnb.sql"))
    client.post("/sessions", data={
        'email': 'alice@example.com',
        'password': 'password123',
    })
    response = client.post("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data

def test_password_hashes(client, db_connection):
    client.post("/users", data={
        "full_name": "carol",
        "email": "carol@gmail.com",
        "password": "Password234",
        "password_confirmation": "Password234",
        "is_host": "on",
    })
    users = UserRepository(db_connection).all()
    stored_hash = users[-1].password
    assert stored_hash != "Password234"
    assert check_password_hash(stored_hash, "Password234")

def test_user_can_login_with_hashed_password(client):
    client.post("/users", data={
        "full_name": "Carol",
        "email": "carol@gmail.com",
        "password": "Password234",
        "is_host": "on"
    })
    response = client.post("/sessions", data={
        "email": "carol@gmail.com",
        "password": "Password234",
    })
    assert response.headers["Location"] == "/spaces"

def test_login_rejects_incorrect_password(client):
    client.post("/users", data={
        "full_name": "Carol",
        "email": "carol@gmail.com",
        "password": "Password234",
        "is_host": "on"
    })
    response = client.post("/sessions", data={
        "email": "carol@gmail.com",
        "password": "incorrect",
    })
    assert response.headers["Location"] == "/login"
    with client.session_transaction() as session:
        assert "user_id" not in session


def test_unauthenticated_user_redirected_from_requests(client, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")

    response = client.get("/requests")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


def test_authenticated_user_can_access_requests(client, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")

    with client.session_transaction() as sess:
        sess["user_id"] = 1  # Log in as Alice

    response = client.get("/requests")

    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Requests" in html

def test_unauthenticated_user_redirected_from_creating_new_spaces_page(client, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")

    response = client.get("/spaces/new")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


def test_authenticated_user_can_access_creating_new_spaces_page(client, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")

    with client.session_transaction() as sess:
        sess["user_id"] = 1  # Log in as Alice

    response = client.get("/spaces/new")

    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "List a Space" in html

def test_create_space_link_only_visible_to_hosts(client, db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")

    # Logged in as host (Alice, user_id=1)
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    host_html = client.get("/spaces").data.decode("utf-8")
    assert "Create Space" in host_html

    # Logged in as non-host guest (e.g. user_id=2)
    with client.session_transaction() as sess:
        sess["user_id"] = 2
    guest_html = client.get("/spaces").data.decode("utf-8")
    assert "Create Space" not in guest_html