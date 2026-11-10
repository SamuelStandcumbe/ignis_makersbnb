class Request:

    def __init__(self, space_id, user_id, approved, id = None):
        self.id = id
        self.space_id = space_id
        self.user_id = user_id
        self.approved = approved

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"Request({self.id}, {self.space_id}, {self.user_id}, {self.approved})"