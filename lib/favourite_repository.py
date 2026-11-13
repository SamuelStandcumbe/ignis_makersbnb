from lib.space import Space

class FavouriteRepository:
    def __init__(self, connection):
        self._connection = connection

    def add(self, user_id, space_id):
        self._connection.execute(
            "INSERT INTO favourites (user_id, space_id) VALUES (%s, %s) ON CONFLICT (user_id, space_id) DO NOTHING",
            [user_id, space_id]
        )

    def remove(self, user_id, space_id):
        self._connection.execute(
            "DELETE FROM favourites WHERE user_id = %s AND space_id = %s",
            [user_id, space_id]
        )

    def find_space_ids_by_user(self, user_id):
        rows = self._connection.execute(
            "SELECT space_id FROM favourites WHERE user_id = %s",
            [user_id]
        )
        return {row["space_id"] for row in rows}

    def find_spaces_by_user(self, user_id):
        rows = self._connection.execute(
            """
            SELECT spaces.*
            FROM spaces
            JOIN favourites ON favourites.space_id = spaces.id
            WHERE favourites.user_id = %s
            ORDER BY favourites.id DESC
            """,
            [user_id]
        )
        return [
            Space(
                row["space_name"],
                row["location"],
                row["description"],
                row["price"],
                row["user_id"],
                row["id"]
            )
            for row in rows
        ]