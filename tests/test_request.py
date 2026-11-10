from lib.request import Request

#test that request instances with the correct variables
def test_request_instancing():
    request = Request(1, 2, False, '2026-10-10')
    assert request.space_id == 1
    assert request.user_id == 2
    assert request.approved is False
    assert request.requested_date == '2026-10-10'
    assert request.id is None

#test that request can instance when given an id
def test_request_instancing_with_id():
    request = Request(1, 2, False, '2026-10-10', 1)
    assert request.id == 1

#test two users with identical attributes are equal
def test_requestss_are_equal_when_attributes_match():
    a = Request(1, 2, False, '2026-10-10')
    b = Request(1, 2, False, '2026-10-10')
    assert a == b

#test readable string format
def test_requests_repr():
    request = Request(1, 2, False, '2026-10-10', 1)
    assert repr(request) == "Request(1, 2, False, 2026-10-10, 1)"