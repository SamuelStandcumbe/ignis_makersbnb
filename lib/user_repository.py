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

    def find_by_email_address(self, email_address):
        rows = self._connection.execute('SELECT * FROM users WHERE email = %s', [email_address])
        if not rows:
            return None
        else:
            user_details = rows[0]
        return User (user_details["username"], user_details["email"], user_details["password"], user_details["host"], user_details["id"] )