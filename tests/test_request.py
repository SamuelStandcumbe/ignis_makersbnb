from datetime import date
from lib.request import Request

#test that request instances with the correct variables
def test_request_instancing():
    request = Request(1, 2, 'pending', date(2026, 10, 10), date(2026, 10, 10), 1)
    assert request.space_id == 1
    assert request.user_id == 2
    assert request.approved_status == 'pending'
    assert request.start_date == date(2026, 10, 10)
    assert request.end_date == date(2026, 10, 10)
    assert request.host_id == 1
    assert request.id is None

#test identical users match
def test_equality():
    a = Request(1, 1, 2, True, date(2026, 10, 10), date(2026, 10, 12))
    b = Request(1, 1, 2, True, date(2026, 10, 10), date(2026, 10, 12))
    assert a == b

#test readable string format
def test_requests_repr():
    request = Request(1, 2, False, date(2026, 10, 10), date(2026, 10, 12), 1, 1)
    assert repr(request) == "Request(1, 2, False, 2026-10-10, 2026-10-12, 1, 1, False, None)"

#test date range is valid
def test_date_within_range_is_valid():
    request = Request(1, 1, True, date(2026, 11, 12), date(2026, 11, 14), 1)
    assert request.generate_errors() == []

#test one day boking still works
def test_one_day_booking():
    request = Request(1, 1, True, date(2026, 11, 12), date(2026, 11, 12), 1)
    assert request.generate_errors() == []

#test end date before start date is invalid
def test_end_date_before_start_date_invalid():
    request = Request(1, 1, True, date(2026, 11, 13), date(2026, 11, 12), 1)
    assert request.generate_errors() == ["End date cannot be before start date"]
    assert request.is_valid() == False

#test dates cover everey date in range
def test_dates_covers_every_date_in_range():
    request = Request(1, 1, True, date(2026, 11, 12), date(2026, 11, 14), 1)
    assert request.dates() == [date(2026, 11, 12), date(2026, 11, 13), date(2026, 11, 14)]

# test one day booking has one date
def test_one_day_booking_has_one_date():
    request = Request(1, 1, True, date(2026, 11, 12), date(2026, 11, 12), 1)
    assert request.dates() == [date(2026, 11, 12)]

# test dates work across a month boundary
def test_dates_in_different_months():
    request = Request(1, 1, True, date(2026, 12, 30), date(2027, 1, 2), 1)
    assert request.dates() == [date(2026, 12, 30), date(2026, 12, 31), date(2027, 1, 1), date(2027, 1, 2)]

# Test that request can instance when given an id
def test_request_instancing_with_id():
    request = Request(1, 2, False, date(2026, 10, 10), date(2026, 10, 12), 1, 1)
    assert request.id == 1
    assert request.paid == False
    assert request.stripe_session_id is None

