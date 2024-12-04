from datetime import datetime, time
from typing import List, Optional


class Package:
    def __init__(self, package_id: int, address: str, deadline: str,
                 city: str, zip_code: str, weight: str):
        # Core package data
        self.package_id = package_id
        self.address = address
        self.original_address = address
        self.corrected_address = None
        self.deadline = self._parse_deadline(deadline) 
        self.city = city
        self.zip_code = zip_code
        self.original_zip = zip_code  
        self.corrected_zip = None         
        self.weight = weight

        # Status and Tracking
        self.status = "At Hub"
        self.delivery_time = None
        self.departure_time = None
        self.special_notes = None
        self.truck_id = None
        
        # special handling attributes
        self.delayed_until = None
        self.required_truck = None
        self.grouped_with: List[int] = []
        self.wrong_address = False

    def mark_en_route(self, departure_time: datetime, truck_id: int) -> None:
        self.status = "En Route"
        self.departure_time = departure_time
        self.truck_id = truck_id

    def mark_delivered(self, delivery_time: datetime) -> None:
        self.status = "Delivered"
        self.delivery_time = delivery_time

    def update_address(self, new_address: str, current_time: datetime) -> None:
        """Store the corrected address but only use it after 10:20 AM"""
        self.corrected_address = new_address
        if current_time.time() >= time(10, 20):
            self.address = new_address
            self.special_notes = f"Address updated at {current_time}"

    def update_zip(self, new_zip: str, current_time: datetime) -> None:
        """Store the corrected zip but only use it after 10:20 AM"""
        self.corrected_zip = new_zip
        if current_time.time() >= time(10, 20):
            self.zip_code = new_zip

    def get_current_address(self, current_time: datetime) -> str:
        """Get the appropriate address based on the current time"""
        if self.wrong_address:
            if current_time.time() >= time(10, 20) and self.corrected_address:
                return self.corrected_address
            return self.original_address
        return self.address
    
    def get_current_zip(self, current_time: datetime) -> str:
        """Get the appropriate zip code based on the current time"""
        if self.wrong_address:
            if current_time.time() >= time(10, 20) and self.corrected_zip:
                return self.corrected_zip
            return self.original_zip
        return self.zip_code

    def _parse_deadline(self, deadline: str) -> time:
        """Convert deadline string to time object"""
        if deadline == "EOD":
            return time(17, 0) 
        try:
            return datetime.strptime(deadline, "%I:%M %p").time()
        except ValueError:
            return time(17, 0) 
        
    def can_be_loaded(self, current_time: datetime, truck_id: int) -> bool:
        """Check if package can be loaded on truck"""
        # Check if delayed
        if self.delayed_until and current_time.time() < self.delayed_until:
            return False
            
        # Check if wrong address not fixed
        if self.wrong_address and current_time.time() < time(10, 20):
            return False
            
        # Check truck restriction
        if self.required_truck and self.required_truck != truck_id:
            return False
            
        return True
