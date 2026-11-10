from lib.space import Space

class SpaceRepository:
    def __init__(self, connection):
        self._connection = connection

    def find_by_space_id(self, space_id):
        rows = self._connection.execute(
            'SELECT * FROM spaces WHERE id = %s', [space_id])
        if rows:
            row = rows[0]
            return Space(row["id"], row["space_name"], row["location"], row["description"], row["price"], row["user_id"])
        else: 
            return None