from typing import List, Optional
from datetime import datetime, timedelta
from .package import Package
from .distance_table import DistanceTable

class Truck:
    """
    Represents a delivery truck with package handling capabilities.
    Constraints:
        - Max 16 packages per truck
        - Travels at 18 mph
        - Infinite gas/no stops needed
    """
    
    # Status Constants
    STATUS_AT_HUB = "At Hub"
    STATUS_EN_ROUTE = "En Route"
    HUB_ADDRESS = "4001 South 700 East"


    def __init__(self, truck_id: int, start_time: datetime):
        # Constants
        self.SPEED = 18  # Miles per hour
        self.MAX_CAPACITY = 16  # Max packages per truck

        # truck properties
        self.truck_id: int = truck_id
        self.packages: List[Package] = []
        self.current_address = self.HUB_ADDRESS
        self.status = self.STATUS_AT_HUB
        self.mileage = 0.0
        self.current_time = start_time

    def load_package(self, package: Package) -> bool:
        """
        Load a package into the truck if there's capacity
        Returns: True if loaded, False if truck full
        """
        if len(self.packages) < self.MAX_CAPACITY:
            self.packages.append(package)
            package.mark_en_route(self.current_time)
            return True
        return False
    
    def find_nearest_package(self, distance_table: DistanceTable) -> Optional[Package]:
        """
        Find the nearest package from current location
        Args:
            distance_table: Table of distances between locations
        Returns:
            Nearest package or None if no packages left
        """
        nearest_package = None
        shortest_distance = float("inf") #start with infinity

        # check each package on truck
        for package in self.packages:
            if package.status != "Delivered":
                # Get distance to this packages delivery address
                distance = distance_table.get_distance(self.current_address, package.address)
            
            # if this is closer than what we've found so far
            if distance < shortest_distance:
                shortest_distance = distance
                nearest_package = package
            
        return nearest_package
    
    


    