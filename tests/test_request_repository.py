from lib.request_repository import RequestRepository
import datetime

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