from lib.request import Request
from lib.request_repository import RequestRepository

#test that all returns every request
def test_all_returns_requests_for_user(db_connection, user_id):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = RequestRepository(db_connection)
    assert repo.find_by_user(2) == [
        Request("Alice Example", "alice@example.com", "password123", True, 1),
        Request("Bob Example", "bob@example.com", "password456", False, 2),
    ]

