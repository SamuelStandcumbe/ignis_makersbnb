from datetime import date, timedelta
from lib.request import Request
from lib.request_repository import RequestRepository

NEXT_WEEK = date.today() + timedelta(days=7)
NEXT_WEEK_PLUS_2 = NEXT_WEEK + timedelta(days=2)

# Seed data: Alice (1) owns spaces 1-3. Bob (2) is a guest there.
# Counts are taken before and after, so tests don't depend on how many seeded requests there are.

def log_in_as(client, user_id):
    with client.session_transaction() as session:
        session["user_id"] = user_id

def all_requests(db_connection):
    return db_connection.execute("SELECT * FROM requests ORDER BY id")

def add_guest(db_connection, name):
    rows = db_connection.execute(
        "INSERT INTO users (full_name, email, password, host) VALUES (%s, %s, 'pw', FALSE) RETURNING id",
        [name, f"{name}@example.com"])
    return rows[0]["id"]

def book(client, space_id, start, end=None):
    data = {"start_date": str(start)}
    if end is not None:
        data["end_date"] = str(end)
    return client.post(f"/make_request/{space_id}", data=data)


# --- 1. Repository: saves guest, space, host, dates and pending status ---

def test_create_saves_every_field(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    RequestRepository(db_connection).create(Request(
        space_id=3, user_id=2, approved_status='pending',
        start_date=NEXT_WEEK, end_date=NEXT_WEEK_PLUS_2, host_id=1))
    last = all_requests(db_connection)[-1]
    assert last["space_id"] == 3
    assert last["user_id"] == 2
    assert last["host_id"] == 1
    assert last["start_date"] == NEXT_WEEK
    assert last["end_date"] == NEXT_WEEK_PLUS_2
    assert last["approved_status"] == 'pending'


# --- 2. A logged-in guest can send a request and sees a confirmation ---

def test_guest_can_request_a_range_and_sees_confirmation(client, db_connection):
    log_in_as(client, 2)
    response = book(client, 1, NEXT_WEEK, NEXT_WEEK_PLUS_2)
    assert response.status_code == 302
    assert response.headers["Location"] == "/requests"

    page = client.get("/requests").get_data(as_text=True)
    assert "Request sent!" in page
    assert "pending" in page

    last = all_requests(db_connection)[-1]
    assert last["space_id"] == 1
    assert last["user_id"] == 2
    assert last["host_id"] == 1
    assert last["start_date"] == NEXT_WEEK
    assert last["end_date"] == NEXT_WEEK_PLUS_2
    assert last["approved_status"] == 'pending'

def test_leaving_end_date_blank_books_one_night(client, db_connection):
    log_in_as(client, 2)
    book(client, 1, NEXT_WEEK)
    last = all_requests(db_connection)[-1]
    assert last["start_date"] == NEXT_WEEK
    assert last["end_date"] == NEXT_WEEK


# --- 3. Logged-out users are sent to log in ---

def test_logged_out_user_is_sent_to_login(client, db_connection):
    before = len(all_requests(db_connection))
    response = book(client, 1, NEXT_WEEK)
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"
    assert len(all_requests(db_connection)) == before


# --- 4. Nights already confirmed are rejected ---

def test_cannot_request_nights_that_overlap_a_booking(client, db_connection):
    RequestRepository(db_connection).create(Request(
        space_id=1, user_id=2, approved_status='approved',
        start_date=NEXT_WEEK, end_date=NEXT_WEEK_PLUS_2, host_id=1))
    before = len(all_requests(db_connection))
    log_in_as(client, 2)
    # starts the night before and runs into the booked range
    response = book(client, 1, NEXT_WEEK - timedelta(days=1), NEXT_WEEK)
    assert response.status_code == 400
    assert "already booked" in response.get_data(as_text=True)
    assert len(all_requests(db_connection)) == before


# --- 5. Past dates, dates beyond the calendar range, and bad ranges are rejected ---

def test_cannot_request_nights_in_the_past(client, db_connection):
    before = len(all_requests(db_connection))
    log_in_as(client, 2)
    response = book(client, 1, date.today() - timedelta(days=1), NEXT_WEEK)
    assert response.status_code == 400
    assert "in the past" in response.get_data(as_text=True)
    assert len(all_requests(db_connection)) == before

def test_cannot_request_nights_more_than_a_year_ahead(client, db_connection):
    before = len(all_requests(db_connection))
    log_in_as(client, 2)
    response = book(client, 1, NEXT_WEEK, date.today() + timedelta(days=366))
    assert response.status_code == 400
    assert "up to a year ahead" in response.get_data(as_text=True)
    assert len(all_requests(db_connection)) == before

def test_end_date_before_start_date_is_rejected(client, db_connection):
    before = len(all_requests(db_connection))
    log_in_as(client, 2)
    response = book(client, 1, NEXT_WEEK_PLUS_2, NEXT_WEEK)
    assert response.status_code == 400
    assert "End date cannot be before start date" in response.get_data(as_text=True)
    assert len(all_requests(db_connection)) == before

def test_cannot_request_without_a_start_date(client, db_connection):
    before = len(all_requests(db_connection))
    log_in_as(client, 2)
    response = client.post("/make_request/1", data={"start_date": ""})
    assert response.status_code == 400
    assert "Please pick a start date" in response.get_data(as_text=True)
    assert len(all_requests(db_connection)) == before


# --- 6. Pending requests don't block other guests ---

def test_two_guests_can_request_the_same_pending_nights(client, db_connection):
    carol = add_guest(db_connection, "carol")
    log_in_as(client, 2)
    book(client, 1, NEXT_WEEK, NEXT_WEEK_PLUS_2)
    log_in_as(client, carol)
    response = book(client, 1, NEXT_WEEK, NEXT_WEEK_PLUS_2)

    assert response.status_code == 302
    same_nights = [r for r in all_requests(db_connection)
    if r["space_id"] == 1 and r["start_date"] == NEXT_WEEK]
    assert sorted(r["user_id"] for r in same_nights) == [2, carol]
    assert all(r["approved_status"] == 'pending' for r in same_nights)


# --- 7. The host comes from the space's owner, not the form ---

def test_host_cannot_be_set_through_the_form(client, db_connection):
    log_in_as(client, 2)
    client.post("/make_request/1", data={"start_date": str(NEXT_WEEK), "host_id": "2"})
    assert all_requests(db_connection)[-1]["host_id"] == 1  # Alice owns space 1


# --- Extras ---

def test_requesting_a_space_that_does_not_exist_gives_404(client):
    log_in_as(client, 2)
    response = book(client, 999, NEXT_WEEK)
    assert response.status_code == 404

def test_booking_page_shows_the_request_form(client):
    html = client.get("/make_request/1").get_data(as_text=True)
    assert '<form action="/make_request/1" method="POST">' in html
    assert 'name="start_date"' in html
    assert 'name="end_date"' in html
