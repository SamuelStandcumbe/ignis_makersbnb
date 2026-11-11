from lib.request import Request

class RequestRepository:
    def __init__(self, connection):
        self._connection = connection

    #moved the filter to the sql
    #each approved booking is put into request.dates
    def find_unavailable_dates_by_space_id(self, space_id):
        rows = self._connection.execute(
            'SELECT * FROM requests WHERE space_id = %s AND approved = TRUE ORDER BY start_date' , [space_id])
        unavailable_dates = []
        for row in rows:
            request = Request(
                row["space_id"],
                row["user_id"],
                row["approved"],
                row["start_date"],
                row["end_date"],
                row["host_id"],
                row["id"]
            )
            unavailable_dates.extend(request.dates())
        return unavailable_dates

    #function to see if there is overlap in the requested dates - requested and booked/unavailable. 
    def has_overlap(self, space_id, start_date, end_date):
        rows = self._connection.execute(
            'SELECT id FROM requests WHERE space_id = %s AND approved = True'
            'AND start_date <= %s AND end_date >= %s',
            [space_id, end_date, start_date])
        return len(rows) > 0 #only returns true if there is overlap - otherwise False
    def approve_request(self, request_id):
        self._connection.execute(
            "UPDATE requests SET approved = True WHERE id = %s;", [request_id]
        )

    def reject_request(self, request_id):
        self._connection.execute(
            "DELETE FROM requests WHERE id = %s;", [request_id]
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
                row["approved"],
                row["start_date"],
                row["end_date"],
                row["host_id"],
                row["id"]
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
                row["approved"],
                row["start_date"],
                row["end_date"],
                row["host_id"],
                row["id"]
            )
            for row in rows
        ]