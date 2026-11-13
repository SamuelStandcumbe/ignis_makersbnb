from lib.request import Request
from lib.request_repository import RequestRepository
import datetime
import pytest

# test that find_by_user returns no requests for a host with none
def test_all_returns_requests_for_host_no_requests(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    db_connection.execute("DELETE FROM requests WHERE host_id = %s", [2])

    repo = RequestRepository(db_connection)

    assert repo.find_by_user(2) == []

# test that find_by_user returns every request received by a host
def test_all_returns_requests_for_host_with_requests(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_by_user(1) == [
        Request(1, 2, 'pending', datetime.date(2026, 10, 10), datetime.date(2026, 10, 12), 1, 1),
        Request(2, 2, 'approved', datetime.date(2026, 11, 28), datetime.date(2026, 11, 30), 1, 2),
        Request(2, 2, 'approved', datetime.date(2026, 11, 25), datetime.date(2026, 11, 27), 1, 3),
    ]

# test that approved ranges are expanded into every unavailable date
def test_find_unavailable_dates_by_space_id(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_unavailable_dates_by_space_id(2) == [
        datetime.date(2026, 11, 25), datetime.date(2026, 11, 26),
        datetime.date(2026, 11, 27),
        datetime.date(2026, 11, 28), datetime.date(2026, 11, 29),
        datetime.date(2026, 11, 30),
    ]

def test_find_unavailable_dates_by_space_id_pending_approval(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_unavailable_dates_by_space_id(1) == []

def test_find_unavailable_dates_by_space_id_with_no_requests(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_unavailable_dates_by_space_id(3) == []

# test that find_request_by_id returns a single request
def test_find_by_id_returns_correct_entry(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    request = repo.find_request_by_id(1)
    assert request == Request(
        1,
        2,
        'pending',
        datetime.date(2026, 10, 10),
        datetime.date(2026, 10, 12),
        1,
        1
    )

def test_find_by_id_returns_none_when_not_found(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_request_by_id(999) is None

# test that a new request is saved, unpaid by default
def test_create_saves_a_request_as_unpaid(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    new_request = repo.create(Request(
        1, 2, 'pending', datetime.date(2027, 1, 5), datetime.date(2027, 1, 8), 1
    ))
    assert new_request.id == 5
    saved = repo.find_request_by_id(5)
    assert saved.paid == False
    assert saved.stripe_session_id is None

# test that mark_as_paid flips the flag and stores the Stripe session id
def test_mark_as_paid_sets_paid_and_session_id(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_request_by_id(3).paid == False
    repo.mark_as_paid(3, "cs_test_123")
    request = repo.find_request_by_id(3)
    assert request.paid == True
    assert request.stripe_session_id == "cs_test_123"

def test_request_can_be_approved(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)

    repo.update_request_status(1, "approved")

    assert repo.find_request_by_id(1).approved_status == "approved"


def test_request_can_be_declined_without_being_deleted(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)

    repo.update_request_status(1, "declined")

    request = repo.find_request_by_id(1)
    assert request is not None
    assert request.approved_status == "declined"


def test_resolved_request_cannot_be_changed(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)

    with pytest.raises(ValueError):
        repo.update_request_status(2, "declined")

    assert repo.find_request_by_id(2).approved_status == "approved"


def test_invalid_status_is_rejected(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)

    with pytest.raises(ValueError):
        repo.update_request_status(1, "cancelled")


def test_request_status_visible_to_guest_and_host(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)

    guest_requests = repo.find_requests_made_by_user(2)
    host_requests = repo.find_by_user(1)

    assert any(r.id == 1 and r.approved_status == "pending" for r in guest_requests)
    assert any(r.id == 1 and r.approved_status == "pending" for r in host_requests)