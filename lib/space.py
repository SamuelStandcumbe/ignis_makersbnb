class Space:
    def __init__(self, id, space_name, location, description, price, user_id):
        self.id = id
        self.space_name = space_name
        self.location = location
        self.description = description
        self.price = price
        self.user_id = user_id

    def is_valid(self):
        return self.generate_errors() == []

    def generate_errors(self):
        errors = []

        if not self.space_name:
            errors.append("Name is required")

        if not self.location:
            errors.append("Location is required")

        if not self.description:
            errors.append("Description is required")

        if self.price in (None, ""):
            errors.append("Price is required")
        else:
            try:
                if float(self.price) <= 0:
                    errors.append("Price must be more than 0")
            except ValueError:
                errors.append("Price must be a number")

        return errors

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"Space({self.id}, {self.space_name}, {self.location}, {self.description}, {self.price}, {self.user_id})"