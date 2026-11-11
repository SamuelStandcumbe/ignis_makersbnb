
from lib.request import Request
from lib.request_repository import RequestRepository
import datetime

#test that all returns every request
def test_all_returns_requests_for_host_no_requests(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_by_user(2) == []

def test_all_returns_requests_for_host_with_requests(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_by_user(1) == [Request(1, 2, False, datetime.date(2026, 10, 10), 1, 1),
                                    Request(2, 2, True, datetime.date(2026, 11, 28), 1, 2),
                                    Request(2, 2, True, datetime.date(2026, 11, 25), 1, 3),]

def test_find_unavailable_dates_by_space_id(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_unavailable_dates_by_space_id(1) == []
    
def test_find_unavailable_dates_by_space_id_pending_approval(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_unavailable_dates_by_space_id(1) == []

def test_find_unavailable_dates_by_space_id_with_no_requests(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_unavailable_dates_by_space_id(3) == []

def test_find_by_id_returns_correct_entry(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    request = repo.find_request_by_id(1)
    assert request[0] == Request(1, 2, False, datetime.date(2026, 10, 10), 1, 1)

def test_appprove_request_changes_entry_to_true(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    repo.approve_request(1)
    request = repo.find_request_by_id(1)
    assert request[0].approved == True

def test_reject_request_removes_entry(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    repo.reject_request(1)
    request = repo.find_request_by_id(1)
    assert request == []



