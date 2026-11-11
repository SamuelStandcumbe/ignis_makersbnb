class Request:
    def __init__(self, id, space_id, user_id, approved, requested_date):
        self.id = id
        self.space_id = space_id
        self.user_id = user_id
        self.approved = approved
        self.requested_date = requested_date

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"Request({self.id}, {self.space_id}, {self.user_id}, {self.approved}, {self.requested_date})"