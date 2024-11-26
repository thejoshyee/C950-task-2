from datetime import datetime


class Package:
    def __init__(self, package_id: int, address: str, deadline: str,
                 city: str, zip_code: str, weight: str):
        # Core package data
        self.package_id = package_id
        self.address = address
        self.deadline = deadline
        self.city = city
        self.zip_code = zip_code
        self.weight = weight

        # Status and Tracking
        self.status = "At Hub"
        self.delivery_time = None
        self.departure_time = None
        self.special_notes = None

    def mark_en_route(self, departure_time):
        self.status = "En Route"
        self.departure_time = departure_time

    def mark_delivered(self, delivery_time):
        self.status = "Delivered"
        self.delivery_time = delivery_time

    def update_address(self, new_address, current_time):
        # Only update if the its after 10:20am
        update_time = datetime.strptime("10:20:00", "%H:%M:%S").time()
        if current_time >= update_time:  # Changed from > to >=
            self.address = new_address
            self.special_notes = f"Address updated at {current_time}"

