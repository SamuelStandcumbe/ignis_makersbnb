from lib.space_repository import SpaceRepository
from decimal import Decimal
from lib.space import Space

def test_list_all_spaces(db_connection):
    db_connection.seed('seeds/ignis_makersbnb.sql')
    repo = SpaceRepository(db_connection)
    assert repo.all() == [
        Space("Fisherman's cottage by the harbour", 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.', Decimal('95.00'), 1, 1),
        Space('Stone barn in the Peak District', 'Edale, Derbyshire', 'Converted barn at the start of the Pennine Way. Boot room, drying rack and a big kitchen table.', Decimal('140.00'), 1, 2),
        Space('Bright studio near Brick Lane', 'Shoreditch, London', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.', Decimal('120.00'), 1, 3),
        Space('Coastal Retreat', 'Deal, Kent', 'A cosy seaside cottage with beautiful coastal views.', Decimal('110.00'), 2, 4)
    ]


def test_find_by_space_id(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = SpaceRepository(db_connection)
    assert repo.find_by_space_id(1) == Space(
        "Fisherman's cottage by the harbour",
        "Whitstable, Kent",
        "Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.",
        Decimal('95.00'),
        1,
        1
    )

def test_find_by_search_term(db_connection):
    db_connection.seed("seeds/ignis_makersbnb.sql")
    repo = SpaceRepository(db_connection)
    assert repo.find_by_search("London") == [Space('Bright studio near Brick Lane',
        'Shoreditch, London',
        'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.',
        120.00,
        1,
        3
    )]