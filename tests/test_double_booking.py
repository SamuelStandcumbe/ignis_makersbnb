from datetime import date, timedelta
import psycopg
import pytest
import threading
import time
from lib.request_repository import RequestRepository

NEXT_MONTH = date.today() + timedelta(days=30)

# Seed data: Alice (1) owns spaces 1-3. Bob (2) is a guest.

def add_request(db, space_id, user_id, start, end, approved_status='pending'):
    rows = db.execute(
        "INSERT INTO requests (space_id, user_id, approved_status, start_date, end_date, host_id) "
        "VALUES (%s, %s, %s, %s, %s, 1) RETURNING id",
        [space_id, user_id, approved_status, start, end])
    return rows[0]["id"]

def is_approved_status(db, request_id):
    return db.execute("SELECT approved_status FROM requests WHERE id = %s", [request_id])[0]["approved_status"]

def add_guest(db, name):
    rows = db.execute(
        "INSERT INTO users (full_name, email, password, host) VALUES (%s, %s, 'pw', FALSE) RETURNING id",
        [name, f"{name}@example.com"])
    return rows[0]["id"]


# 1. A host can approve a request when the dates are free

def test_host_can_approve_when_dates_are_free(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    request_id = add_request(db_connection, 1, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2))
    RequestRepository(db_connection).update_request_status(request_id, 'approved')
    assert is_approved_status(db_connection, request_id) == 'approved'


# 2. A host can't approve a request that overlaps an approved booking

def test_cannot_approve_when_dates_are_already_booked(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    carol = add_guest(db_connection, "carol")
    add_request(db_connection, 1, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2), approved_status='approved')
    clashing = add_request(db_connection, 1, carol, NEXT_MONTH + timedelta(days=2), NEXT_MONTH + timedelta(days=4))
    repo = RequestRepository(db_connection)
    with pytest.raises(ValueError):
        repo.update_request_status(clashing, 'approved')
    assert is_approved_status(db_connection, clashing) == 'pending'

# 3. A failed approval leaves the request pending


def test_failed_approval_leaves_request_pending(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    carol = add_guest(db_connection, "carol")
    add_request(db_connection, 1, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2), approved_status='approved')
    clashing = add_request(db_connection, 1, carol, NEXT_MONTH + timedelta(days=2), NEXT_MONTH + timedelta(days=4))
    repo = RequestRepository(db_connection)
    with pytest.raises(ValueError):
        repo.update_request_status(clashing, 'approved')
    assert is_approved_status(db_connection, clashing) == 'pending'


# 4. The host is told why approval failed

def test_host_sees_message_when_approval_fails(client, db_connection):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    carol = add_guest(db_connection, "carol")
    add_request(db_connection, 1, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2), approved_status='approved')
    clashing = add_request(db_connection, 1, carol, NEXT_MONTH, NEXT_MONTH)

    response = client.post(f"/requests/{clashing}/approve")
    assert response.status_code == 302
    assert response.headers["Location"] == "/requests"

    page = client.get("/requests").get_data(as_text=True)
    assert "already booked" in page
    assert is_approved_status(db_connection, clashing) == 'pending'


# 5. Two competing approvals can't both succeed

def test_database_refuses_a_second_overlapping_approval(db_connection):
    # Even if the app's check is skipped, the database rule blocks the double booking
    db_connection.seed("seeds/ignis_makersbnb.sql")
    first = add_request(db_connection, 1, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2))
    second = add_request(db_connection, 1, 2, NEXT_MONTH + timedelta(days=1), NEXT_MONTH + timedelta(days=3))
    db_connection.execute("UPDATE requests SET approved_status = 'approved' WHERE id = %s", [first])
    with pytest.raises(psycopg.errors.ExclusionViolation):
        db_connection.execute("UPDATE requests SET approved_status = 'approved' WHERE id = %s", [second])
    db_connection.connection.rollback()
    assert is_approved_status(db_connection, second) == 'pending'


def test_only_one_overlapping_request_can_be_approved(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    first = add_request(
        db_connection, 1, 2,
        NEXT_MONTH, NEXT_MONTH + timedelta(days=2)
    )
    second = add_request(
        db_connection, 1, 2,
        NEXT_MONTH + timedelta(days=1), NEXT_MONTH + timedelta(days=3)
    )
    repo = RequestRepository(db_connection)
    # First approval succeeds
    repo.update_request_status(first, 'approved')
    # Second approval fails because the dates overlap
    with pytest.raises(ValueError):
        repo.update_request_status(second, 'approved')
    # Confirm both requests have the correct statuses
    assert is_approved_status(db_connection, first) == 'approved'
    assert is_approved_status(db_connection, second) == 'pending'

def test_two_hosts_approving_at_the_same_moment(db_connection):
    # Two browsers = two database connections. B tries to approve while A's approval
    # is still in progress (not committed). B has to wait, then gets refused.
    db_connection.seed("seeds/ignis_makersbnb.sql")
    first = add_request(db_connection, 1, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2))
    second = add_request(db_connection, 1, 2, NEXT_MONTH + timedelta(days=1), NEXT_MONTH + timedelta(days=3))

    conn_a = psycopg.connect(db_connection.connection.info.dsn)
    conn_b = psycopg.connect(db_connection.connection.info.dsn)
    conn_a.execute("UPDATE requests SET approved_status = 'approved' WHERE id = %s", [first])  # in progress

    outcome = {}
    def approve_second():
        try:
            conn_b.execute("UPDATE requests SET approved_status = 'approved' WHERE id = %s", [second])
            conn_b.commit()
            outcome["b"] = "approved_status"
        except psycopg.errors.ExclusionViolation:
            conn_b.rollback()
            outcome["b"] = "refused"

    b = threading.Thread(target=approve_second)
    b.start()
    time.sleep(0.5)
    assert b.is_alive()          # B is stuck waiting for A to finish
    conn_a.commit()              # A finishes first...
    b.join(timeout=5)
    conn_a.close(); conn_b.close()

    assert outcome["b"] == "refused"   # ...so B is refused
    assert is_approved_status(db_connection, first) == 'approved'
    assert is_approved_status(db_connection, second) == 'pending'


# 6. Requests for different dates can still be approved independently

def test_requests_for_different_dates_can_both_be_approved(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    first = add_request(db_connection, 1, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2))
    later = add_request(db_connection, 1, 2, NEXT_MONTH + timedelta(days=3), NEXT_MONTH + timedelta(days=5))
    repo = RequestRepository(db_connection)
    repo.update_request_status(first, 'approved')
    repo.update_request_status(later, 'approved')
    assert is_approved_status(db_connection, first) == 'approved'
    assert is_approved_status(db_connection, later) == 'approved'

def test_same_dates_at_a_different_space_can_both_be_approved(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    cottage = add_request(db_connection, 1, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2))
    studio = add_request(db_connection, 3, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2))
    repo = RequestRepository(db_connection)
    repo.update_request_status(cottage, 'approved')
    repo.update_request_status(studio, 'approved')
    assert is_approved_status(db_connection, cottage) == 'approved'
    assert is_approved_status(db_connection, studio) == 'approved'


# Pending requests are still allowed to overlap (out of scope to block them)

def test_pending_requests_can_still_overlap(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    add_request(db_connection, 1, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2))
    add_request(db_connection, 1, 2, NEXT_MONTH, NEXT_MONTH + timedelta(days=2))
    count = db_connection.execute(
        "SELECT COUNT(*) AS n FROM requests WHERE space_id = 1 AND start_date = %s", [NEXT_MONTH])[0]["n"]
    assert count == 2
