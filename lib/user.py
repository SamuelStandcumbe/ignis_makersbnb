class User():
    def __init__(self, full_name, email, password, host, id=None):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.password = password
        self.host = host

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"User({self.full_name}, {self.email}, {self.password}, {self.host}, {self.id})"