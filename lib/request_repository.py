from lib.request import Request

class RequestRepository:
    def __init__(self, connection):
        self._connection = connection

    def find_unavailable_dates_by_space_id(self, space_id):
        rows = self._connection.execute(
            'SELECT requested_date, approved FROM requests WHERE space_id = %s', [space_id])
        if rows:
            unavailable_dates = []
            for row in rows:
                if row["approved"] == True:
                    unavailable_dates.append(row["requested_date"])
            return unavailable_dates
        return []

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
            "SELECT * FROM requests WHERE user_id = %s ORDER BY id", [user_id]
        )
        return [Request(row["space_id"], row["user_id"], row["approved"], row["requested_date"], row["id"]) for row in rows]
