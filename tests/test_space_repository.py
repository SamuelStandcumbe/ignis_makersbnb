from lib.space_repository import SpaceRepository
from lib.space import Space
from decimal import Decimal

def test_find_by_space_id(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = SpaceRepository(db_connection)
    assert repo.find_by_space_id(1) == Space(
        1,
        "Fisherman's cottage by the harbour",
        "Whitstable, Kent",
        "Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.",
        Decimal('95.00'),
        1
    )