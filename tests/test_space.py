from lib.space import Space

def test_space_init_with_properties():
    space = Space(1, 'Fisherman\'s cottage by the harbour', 'Whitstable, Kent', 'Compact studio with a double bed, kitchenette and fast wifi. Five minutes from Shoreditch High Street station.', 95, 1)
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