class User():
    def __init__(self, username, email, password, host, id=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.host = host

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"User({self.username}, {self.email}, {self.password}, {self.host}, {self.id})"