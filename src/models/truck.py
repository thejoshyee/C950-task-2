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
    HUB_ADDRESS = "Western Governors University" 


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
        """Find nearest undelivered package"""
        nearest_package = None
        shortest_distance = float("inf")

        print(f"\nFinding nearest package from: {self.current_address}")
        
        # Check each package on truck
        for package in self.packages:
            if package.status != "Delivered":
                # Get distance to this package's delivery address
                distance = distance_table.get_distance(
                    self.current_address, 
                    package.address
                )
                print(f"Distance to {package.address}: {distance} miles")
                
                # If this is closer than what we've found so far
                if distance < shortest_distance:
                    shortest_distance = distance
                    nearest_package = package
                    print(f"New nearest package: {package.package_id}")
        
        return nearest_package
    
    def deliver_package(self, package: Package, distance_table: DistanceTable) -> None:
        """
        Deliver a package and update truck's location/mileage/time
        Args:
            package: Package to deliver
            distance_table: Distance lookup table 
        """
        print("\nDelivering package:")
        print(f"From: {self.current_address}")
        print(f"To: {package.address}")
        
        # Get distance to delivery address
        distance = distance_table.get_distance(
            "Western Governors University",  # Try using full WGU name
            package.address
        )
        print(f"Got distance: {distance} miles")

        # update trucks mileage
        self.mileage += distance
        print(f"Updated mileage to: {self.mileage}")

        # update trucks location
        self.current_address = package.address
        print(f"Updated location to: {self.current_address}")

        # update time based on distance (hours = distance / speed)
        time_hours = distance / self.SPEED
        time_delta = timedelta(hours=time_hours)
        self.current_time += time_delta
        print(f"Updated time to: {self.current_time}")

        # mark package as delivered
        package.mark_delivered(self.current_time)
        print(f"Marked package {package.package_id} as {package.status}")


    def run_delivery_route(self, distance_table: DistanceTable) -> None:
        """
        Run the delivery route using nearest neighbor algorithm
        Args:
            distance_table: Distance lookup table
        """
        self.status = self.STATUS_EN_ROUTE

        while True:
            # Find nearest undelivered package
            next_package = self.find_nearest_package(distance_table)
            if not next_package:
                break # no more packages to deliver

            # deliver package
            self.deliver_package(next_package, distance_table)

        # return to hub if delievered everything
        if self.current_address != self.HUB_ADDRESS:
            # get distance back to hub
            distance = distance_table.get_distance(self.current_address, self.HUB_ADDRESS)
            
            # update mileage and time
            self.mileage += distance
            time_hours = distance / self.SPEED
            self.current_time += timedelta(hours=time_hours)

            # update location and status
            self.current_address = self.HUB_ADDRESS
            self.status = self.STATUS_AT_HUB
    


    