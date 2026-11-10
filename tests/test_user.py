from lib.user import USER

#test that user instances with the correct variables
def test_user_instancing():
    user = USER("bob", "bob@gmail.com", "Password123", False)
    assert user.username == "bob"
    assert user.email == "bob@gmail.com"
    assert user.password == "Password123"
    assert user.host is False
    assert user.id is None

#test that user can instance when given an id
def test_user_instancing_with_id():
    user = USER("bob", "bob@gmail.com", "Password123", False, 1)
    assert user.id == 1

#test two users with identical attributes are equal
def test_users_are_equal_when_attributes_match():
    a = USER("bob", "bob@gmail.com", "Password123", False, 1)
    b = USER("bob", "bob@gmail.com", "Password123", False, 1)
    assert a == b

#test readable string format
def test_user_repr():
    user = USER("bob", "bob@gmail.com", "Password123", False, 1)
    assert repr(user) == "USER(bob, bob@gmail.com, Password123, False, 1)"