from datetime import timedelta

class Request:
    def __init__(self, space_id, user_id, approved_status, start_date, end_date, host_id, id=None, paid=False, stripe_session_id=None):
        self.id = id
        self.space_id = space_id
        self.user_id = user_id
        self.approved_status = approved_status
        self.start_date = start_date
        self.end_date = end_date
        self.paid = paid
        self.stripe_session_id = stripe_session_id
        self.host_id = host_id


    # function to error if date range isnt valid
    def generate_errors(self):
        errors = []
        if self.end_date < self.start_date:
            errors.append("End date cannot be before start date")
        return errors

    # function to call generate errors returns it (returns true if there are no errors)
    def is_valid(self):
        return self.generate_errors() == []

    # function to calulate the amount of days booked / all the days booked in date format so that the repo can set them as unavailable
    def dates(self):
        days = (self.end_date - self.start_date).days
        return [self.start_date + timedelta(days=i) for i in range(days + 1)]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"Request({self.space_id}, {self.user_id}, {self.approved_status}, {self.start_date}, {self.end_date}, {self.host_id}, {self.id}, {self.paid}, {self.stripe_session_id})"
