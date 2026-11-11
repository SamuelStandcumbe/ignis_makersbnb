class Request:

    def __init__(self, space_id, user_id, approved, requested_date, host_id, id = None):
        self.id = id
        self.space_id = space_id
        self.user_id = user_id
        self.approved = approved
        self.requested_date = requested_date
        self.host_id = host_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"Request({self.space_id}, {self.user_id}, {self.approved}, {self.requested_date}, {self.host_id}, {self.id})"
