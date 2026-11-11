from app import app
from database_connection import DatabaseConnection
from lib.space import Space
from lib.space_repository import SpaceRepository

def reset_database():
    db = DatabaseConnection(test_mode=True)
    db.connect()
    db.seed("seeds/ignis_makersbnb.sql")
    return db


def logged_in_client():
    app.config["TESTING"] = True
    client = app.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1  # Alice from the seed file
    return client


# --- The Space model ---

def test_space_with_all_fields_is_valid():
    space = Space("Cabin", "Bristol", "Cosy", "75", 1, None)
    assert space.is_valid()

def test_space_without_name_or_price_is_invalid():
    space = Space("", "Bristol", "Cosy", "", 1, None)
    assert space.generate_errors() == ["Name is required", "Price is required"]

def test_price_must_be_a_number():
    space = Space("Cabin", "Bristol", "Cosy", "lots", 1, None)
    assert space.generate_errors() == ["Price must be a number"]


# --- Saving to the database ---

def test_a_user_can_save_more_than_one_space():
    db = reset_database()

    db.execute("DELETE FROM requests WHERE space_id = %s", [4])
    db.execute("DELETE FROM spaces WHERE user_id = %s", [2])

    repo = SpaceRepository(db)
    repo.create(Space("Barn", "York", "Rustic", 50, 2, None))
    repo.create(Space("Loft", "Leeds", "Airy", 80, 2, None))

    spaces = repo.find_by_user(2)
    assert len(spaces) == 2


# --- Logged out ---

def test_logged_out_user_is_redirected_from_create_space_form():
    client = app.test_client()
    response = client.get("/spaces/new")
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

def test_logged_out_user_cannot_post_a_space():
    client = app.test_client()
    response = client.post("/spaces", data={"space_name": "Sneaky", "location": "X", "description": "X", "price": "10"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


# --- Logged in ---

def test_logged_in_user_can_see_create_space_form():
    client = logged_in_client()
    response = client.get("/spaces/new")
    assert response.status_code == 200

def test_posting_a_valid_space_saves_it_and_redirects():
    db = reset_database()
    client = logged_in_client()
    response = client.post("/spaces", data={"space_name": "Treehouse", "location": "Bristol", "description": "Up high", "price": "90"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/spaces"
    names = [space.space_name for space in SpaceRepository(db).find_by_user(1)]
    assert "Treehouse" in names

def test_posting_a_space_with_missing_fields_shows_errors():
    db = reset_database()
    spaces_before = SpaceRepository(db).find_by_user(1)
    client = logged_in_client()
    response = client.post("/spaces", data={"space_name": "", "location": "Bristol", "description": "Up high", "price": ""})
    assert response.status_code == 400
    page = response.get_data(as_text=True)
    assert "Name is required" in page
    assert "Price is required" in page
    spaces_after = SpaceRepository(db).find_by_user(1)
    assert len(spaces_after) == len(spaces_before)

def test_space_is_initialised():
    space = Space('Fishermans cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.' , 95, 1,1)
    assert space.space_name == 'Fishermans cottage by the harbour'
    assert space.location == 'Whitstable, Kent'
    assert space.description == 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.'
    assert space.price == 95
    assert space.user_id == 1
    assert space.id == 1

def test_equal_spaces():
    space1 = Space('Fishermans cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.' , 95, 1,1)
    space2 = Space('Fishermans cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.' , 95, 1,1)
    assert space1 == space2

def test_format_nicely():
    space = Space('Fishermans cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.' , 95, 1,1)
    assert str(space) == 'Space(Fishermans cottage by the harbour, Whitstable, Kent, Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station., 95, 1, 1)'




def test_space_init_with_properties():
    space = Space('Fisherman\'s cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.', 95, 1, 1)
    assert space.id == 1
    assert space.space_name == "Fisherman's cottage by the harbour"
    assert space.location == "Whitstable, Kent"
    assert space.description == "Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station."
    assert space.price == 95
    assert space.user_id == 1

def test_equality():
    space1 = Space(1, 'Fisherman\'s cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.', 95, 1)
    space2 = Space(1, 'Fisherman\'s cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.', 95, 1)
    assert space1 == space2

def test_formats_nicely():
    space = Space(1, 'Fisherman\'s cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.', 95, 1)
    assert str(space) == "Space(1, Fisherman's cottage by the harbour, Whitstable, Kent, Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station., 95, 1)"