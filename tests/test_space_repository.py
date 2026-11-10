from lib.space_repository import *
from decimal import Decimal

def test_list_all_spaces(db_connection):
    db_connection.seed('seeds/ignis_makersbnb.sql')
    repo = SpaceRepository(db_connection)
    assert repo.all() == [
        Space('Fishermans cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.', Decimal('95.00'), 1, 1),
        Space('Stone barn in the Peak District', 'Edale, Derbyshire', 'Converted barn at the start of the Pennine Way. Boot room, drying rack and a big kitchen table.', Decimal('140.00'), 1, 2)
    ]