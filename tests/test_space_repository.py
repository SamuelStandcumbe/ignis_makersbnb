from lib.space_repository import *

def test_list_all_spaces(db_connection):
    db_connection.seed('seeds/ignis_makersbnb')
    repo = SpaceRepository(db_connection)
    assert repo.all() == [
        Space('Fishermans cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.' , 95, 1,1),
        Space('Stone barn in the Peak District', 'Edale, Derbyshire', 'Converted barn at the start of the Pennine Way. Boot room, drying rack and a big kitchen table.', 140, 1, 2)
    ]