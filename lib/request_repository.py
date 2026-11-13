import psycopg
from lib.request import Request

class RequestRepository:
    def __init__(self, connection):
        self._connection = connection

    #moved the filter to the sql
    #each approved_status booking is put into request.dates
    def find_unavailable_dates_by_space_id(self, space_id):
        rows = self._connection.execute(
            "SELECT * FROM requests WHERE space_id = %s AND approved_status = 'approved' ORDER BY start_date" , [space_id])
        unavailable_dates = []
        for row in rows:
            request = Request(
                row["space_id"],
                row["user_id"],
                row["approved_status"],
                row["start_date"],
                row["end_date"],
                row["host_id"],
                row["id"],
                row["paid"],
                row["stripe_session_id"]
            )
            unavailable_dates.extend(request.dates())
        return unavailable_dates

    #function to see if there is overlap in the requested dates - requested and booked/unavailable. 
    def has_overlap(self, space_id, start_date, end_date):
        rows = self._connection.execute(
            "SELECT id FROM requests WHERE space_id = %s AND approved_status = 'approved'"
            'AND start_date <= %s AND end_date >= %s',
            [space_id, end_date, start_date])
        return len(rows) > 0 #only returns true if there is overlap - otherwise False

    # Save a new booking request for one or more nights
    def create(self, booking_request):
        rows = self._connection.execute(
            'INSERT INTO requests (space_id, user_id, approved_status, start_date, end_date, host_id) '
            'VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
            [booking_request.space_id, booking_request.user_id, booking_request.approved_status,
            booking_request.start_date, booking_request.end_date, booking_request.host_id])
        booking_request.id = rows[0]["id"]
        return booking_request

    def update_request_status(self, request_id, new_status):
        request = self.find_request_by_id(request_id)
        if not request:     
            raise ValueError("Booking request does not exist")
        if request.approved_status != 'pending':
            raise ValueError("request has already been resolved")
        if new_status not in ['approved', 'declined']:
            raise ValueError("new status must be 'approved' or 'declined'")
        try:
            rows = self._connection.execute(
                "UPDATE requests SET approved_status = %s WHERE approved_status = 'pending' AND id = %s RETURNING id;", 
                [new_status, request_id]
            )
            if rows == []:
                raise ValueError("nothing was changed")
        except psycopg.errors.ExclusionViolation:
            self._connection.connection.rollback()
            raise ValueError("these dates are already booked")

    def find_request_by_id(self, request_id):
        rows = self._connection.execute(
            "SELECT * FROM requests WHERE id = %s;", [request_id]
        )
        if not rows:
            return None
        row = rows[0]
        return Request(
            row["space_id"],
            row["user_id"],
            row["approved_status"],
            row["start_date"],
            row["end_date"],
            row["host_id"],
            row["id"],
            row["paid"],
            row["stripe_session_id"]
        )

    def find_by_user(self, user_id):
        rows = self._connection.execute(
            "SELECT * FROM requests WHERE host_id = %s ORDER BY id",
            [user_id]
        )
        return [
            Request(
                row["space_id"],
                row["user_id"],
                row["approved_status"],
                row["start_date"],
                row["end_date"],
                row["host_id"],
                row["id"],
                row["paid"],
                row["stripe_session_id"]
            )
            for row in rows
        ]

    def find_requests_made_by_user(self, user_id):
        rows = self._connection.execute(
            "SELECT * FROM requests WHERE user_id = %s ORDER BY id",
            [user_id]
        )
        return [
            Request(
                row["space_id"],
                row["user_id"],
                row["approved_status"],
                row["start_date"],
                row["end_date"],
                row["host_id"],
                row["id"],
                row["paid"],
                row["stripe_session_id"]
            )
            for row in rows
        ]

    #marks a request as paid and saves the stripe session id
    def mark_as_paid(self, request_id, stripe_session_id):
        self._connection.execute(
            "UPDATE requests SET paid = True, stripe_session_id = %s WHERE id = %s;",
            [stripe_session_id, request_id]
        )