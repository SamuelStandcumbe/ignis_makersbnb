from datetime import date
from lib.request import Request

def test_request_init_with_properties():
    request = Request(1, 1, 2, True, date(2026, 10, 10), date(2026, 10, 12))
    assert request.id == 1
    assert request.space_id == 1
    assert request.user_id == 2
    assert request.approved == True
    assert request.start_date == date(2026, 10, 10)
    assert request.end_date == date(2026, 10, 12)

def test_equality():
    request1 = Request(1, 1, 2, True, date(2026, 10, 10), date(2026, 10, 12))
    request2 = Request(1, 1, 2, True, date(2026, 10, 10), date(2026, 10, 12))
    assert request1 == request2

def test_formats_nicely():
    request = Request(1, 1, 2, True, date (2026, 10, 10), date(2026, 10, 12))
    assert str(request) == "Request(1, 1, 2, True, 2026-10-10, 2026-10-12)"

#tests for booking date
#test date range is valid
def test_date_within_range_is_valid():
    request = Request(1, 1, 1, True, date(2026, 11, 12), date(2026, 11, 14))
    assert request.generate_errors() == []

#test one day boking still works
def test_one_day_booking():
    request = Request(1, 1, 1, True, date(2026, 11, 12), date(2026, 11, 12))
    assert request.generate_errors() == []

#test end date before start date is invalid
def test_end_date_before_start_date_invalid():
    request = Request(1, 1, 1, True, date(2026, 11, 13), date(2026, 11, 12))
    assert request.generate_errors() == ["End date cannot be before start date"]
    assert request.is_valid() == False

#test dates cover everey date in range
def test_dates_covers_every_date_in_range():
    request = Request(1, 1, 1, True, date(2026, 11, 12), date(2026, 11, 14))
    assert request.dates() == [date(2026, 11, 12), date(2026, 11, 13), date(2026, 11, 14)]

# test one day booking has one date
def test_one_day_booking_has_one_date():
    request = Request(1, 1, 1, True, date(2026, 11, 12), date(2026, 11, 12))
    assert request.dates() == [date(2026, 11, 12)]

# test dates work across a month boundary
def test_dates_in_different_months():
    request = Request(1, 1, 1, True, date(2026, 12, 30), date(2027, 1, 2))
    assert request.dates() == [date(2026, 12, 30), date(2026, 12, 31), date(2027, 1, 1), date(2027, 1, 2)]