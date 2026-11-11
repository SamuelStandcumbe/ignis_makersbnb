from datetime import date
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

#tests for booking date
#test date range is valid
def test_date_within_range_is_valid():
    request = Request(1, 1, 1, True, date(2026-11-12), date(2026-11-14))
    assert request.generate_errors == []

#test one day boking still works
def test_one_day_booking():
    request = Request(1, 1, 1, True, date(2026-11-12), date(2026-11-12))
    assert request.generate_errors == []

#test end date before start date is valid

#test dates cover everey date in range