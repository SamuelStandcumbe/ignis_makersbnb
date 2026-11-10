from lib.request import Request

class RequestRepository:
    def __init__(self, connection):
        self._connection = connection

    def find_by_user(self, user_id):
        rows = self._connection.execute(
            "SELECT * FROM spaces WHERE user_id = %s ORDER BY id", [user_id]
        )
        return [Request(row["id"], row["space_name"], row["location"], row["description"],
                    row["price"], row["user_id"]) for row in rows]

    def create(self, request):
        rows = self._connection.execute(
            "INSERT INTO spaces (space_name, location, description, price, user_id) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            [request.space_name, request.location, request.description, request.price, request.user_id],
        )
        request.id = rows[0]["id"]
        return request