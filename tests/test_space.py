from lib.space import *

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
    