from lib.user import User
from lib.user_repository import UserRepository

#test that all returns every user
def test_all_returns_users(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = UserRepository(db_connection)
    assert repo.all() == [
        User("Alice Example", "alice@example.com", "password123", True, 1),
        User("Bob Example", "bob@example.com", "password456", False, 2),
    ]

#test create saves a new user to database
def test_create_adds_user(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = UserRepository(db_connection)
    repo.create(User("carol", "carol@gmail.com", "Password234", False, 3))

