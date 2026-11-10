from lib.space import *
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


