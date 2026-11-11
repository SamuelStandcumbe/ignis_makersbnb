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
