
from lib.request import Request
from lib.request_repository import RequestRepository
import datetime

#test that all returns every request
def test_all_returns_requests_for_user(db_connection, user_id):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    pass

def test_find_unavailable_dates_by_space_id(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_unavailable_dates_by_space_id(2) == [datetime.date(2026, 11, 28), datetime.date(2026, 11, 25)]

def test_find_unavailable_dates_by_space_id_pending_approval(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_unavailable_dates_by_space_id(1) == []

def test_find_unavailable_dates_by_space_id_with_no_requests(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_unavailable_dates_by_space_id(3) == []

