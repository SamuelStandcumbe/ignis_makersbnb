from lib.space import *
class SpaceRepository:
    def __init__(self, connection):
        self._connection = connection

    def all(self):
        rows = self._connection.execute('SELECT * FROM spaces')
        available_spaces = []
        for row in rows:
            item = Space(row['space_name'], row['self.location'], row['self.description'], row['self.price'], row['self.user_id'], row['self.id'])
            available_spaces.append(item)
            return available_spaces


