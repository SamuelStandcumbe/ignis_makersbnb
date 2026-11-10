class Space:

    def __init__(self, space_name, location, description, price, user_id, id = None):
        self.id = id
        self.space_name = space_name
        self.location = location
        self.description = description
        self.price = price
        self.user_id = user_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"Space({self.space_name}, {self.location}, {self.description}, {self.price}, {self.user_id}, {self.id})"