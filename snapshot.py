from locations import Location


class Snapshot:
    """
    Represents a parking location with a name, latitude and longitude coordinates, and number of available parking slots
    """
    def __init__(self, name, location, available_slots):
        self.name = name
        self.location = location
        self.available_slots = available_slots

    def __str__(self):
        return f"Name: {self.name}, Location: {self.location} - {self.available_slots} available slots"