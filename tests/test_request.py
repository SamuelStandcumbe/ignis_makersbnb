from lib.request import Request

def test_request_init_with_properties():
    request = Request(1, 1, 2, True, '2026-10-10')
    assert request.id == 1
    assert request.space_id == 1
    assert request.user_id == 2
    assert request.approved == True
    assert request.requested_date == '2026-10-10'

def test_equality():
    request1 = Request(1, 1, 2, True, '2026-10-10')
    request2 = Request(1, 1, 2, True, '2026-10-10')
    assert request1 == request2

def test_formats_nicely():
    request = Request(1, 1, 2, True, '2026-10-10')
    assert str(request) == "Request(1, 1, 2, True, 2026-10-10)"
