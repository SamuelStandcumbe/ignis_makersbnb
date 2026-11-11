from lib.space import Space
class SpaceRepository:
    def __init__(self, connection):
        self._connection = connection

    def all(self):
        rows = self._connection.execute('SELECT * FROM spaces')
        available_spaces = []
        for row in rows:
            item = Space(row['space_name'], row['location'], row['description'], row['price'], row['user_id'], row['id'])
            available_spaces.append(item)
        return available_spaces

    def find_by_space_id(self, space_id):
        rows = self._connection.execute(
            'SELECT * FROM spaces WHERE id = %s', [space_id]
        )

        if rows:
            row = rows[0]
            return Space(
                row["space_name"],
                row["location"],
                row["description"],
                row["price"],
                row["user_id"],
                row["id"]
            )
        else:
            return None

    def find_by_user(self, user_id):
        rows = self._connection.execute(
            "SELECT * FROM spaces WHERE user_id = %s ORDER BY id", [user_id]
        )
        return [Space(row["space_name"], row["location"], row["description"],
                    row["price"], row["user_id"], row["id"]) for row in rows]

    def create(self, space):
        rows = self._connection.execute(
            "INSERT INTO spaces (space_name, location, description, price, user_id) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            [
                space.space_name,
                space.location,
                space.description,
                space.price,
                space.user_id
            ],
        )

        space.id = rows[0]["id"]
        return space