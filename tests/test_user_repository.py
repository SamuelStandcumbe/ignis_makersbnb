from lib.user import User
from lib.user_repository import UserRepository
from werkzeug.security import check_password_hash, generate_password_hash

#test that all returns every user
def test_all_returns_users(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = UserRepository(db_connection)
    result = repo.all()
    assert result[0].full_name == "Alice Example"
    assert result[0].email == "alice@example.com"
    assert result[0].host is True
    assert result[0].id == 1
    assert check_password_hash(result[0].password, "password123")

#test create saves a new user to database
def test_create_adds_user(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = UserRepository(db_connection)
    hashed_password = generate_password_hash("Password234")
    repo.create(User("carol", "carol@gmail.com", hashed_password, False, 3))
    result = repo.all()[-1]
    assert result.full_name == "carol"
    assert result.email == "carol@gmail.com"
    assert result.host is False
    assert result.id == 3
    assert check_password_hash(result.password, "Password234")


# test finds a user using its email address
def test_find_user_by_email(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = UserRepository(db_connection)
    result = repo.find_by_email_address("alice@example.com")
    assert result.full_name == "Alice Example"
    assert result.email == "alice@example.com"
    assert result.host is True
    assert result.id == 1
    assert check_password_hash(result.password, "password123")