from lib.user import User

class UserRepository():
    def __init__(self, connection):
        self._connection = connection

    def all(self):
        rows = self._connection.execute('SELECT * FROM users ORDER BY id')
        users = []
        for row in rows:
            item = User(row["username"], row["email"], row["password"], row["host"], row["id"])
            users.append(item)
        return users

    def create(self, user):
        self._connection.execute(
            'INSERT INTO users (username, email, password, host) VALUES (%s, %s, %s, %s)',
            [user.username, user.email, user.password, user.host]
        )
        return None