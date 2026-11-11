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
            request = Request(row["id"], row["space_id"], row["user_id"], row["approved"], row["start_date"], row["end_date"])
            unavailable_dates.extend(request.dates())

    #function to see if there is overlap in the requested dates - requested and booked/unavailable. 
    def has_overlap(self, space_id, start_date, end_date):
        rows = self._connection.execute(
            'SELECT id FROM requests WHERE space_id = %s AND approved = True',
            'AND start_date <= %s AND end_date >= %s',
            [space_id, end_date, start_date])
        return len(rows) > 0 #only returns true if there is overlap - otherwise False