from datetime import datetime, time, timedelta
from typing import List, Optional
from .distance_table import DistanceTable
from .package_loader import PackageLoader
from .truck import Truck
from .package import Package

class DeliveryService:
    """
    Main Service managing the WGUPS delivery system.
    Handles loading data, assigning packages, and running deliveries.
    """

    def __init__(self):
        """
        Initialize delivery service with required components.
        """
        # Data Management
        self.distance_table = DistanceTable()
        self.package_loader = PackageLoader()

        # Create trucks (all start at 8:00 AM)
        start_time = datetime(2024, 1, 1, 8, 0)
        delayed_start = datetime(2024, 1, 1, 9, 5) 

        self.trucks = [
            Truck(1, start_time),
            Truck(2, start_time),
            Truck(3, delayed_start)
        ]

        # Track stats
        self.total_mileage = 0.0

    def load_data(self, distance_file: str, package_file: str) -> bool:
        """
        Load distance and package data from CSV files.

        Args:
            distance_file: Path to distance data CSV
            package_file: Path to package data CSV
        Returns:
            True if data loaded successfully, False otherwise

        example:
            success = service.load_data("data/distances.csv", "data/packages.csv")
        """
        try:
            # first load distances (needed for routing)
            print("Loading distance data...")
            self.distance_table.load_distance_data(distance_file)

            # then load packages
            print("Loading package data...")
            self.package_loader.load_packages(package_file)

            # verify data loaded
            if not self.distance_table.addresses:
                print("Error: No addresses loaded")
                return False
            
            if not self.package_loader.packages:
                print("Error: No packages loaded")
                return False
            
            print(f"Successfully loaded:")
            print(f"- {len(self.distance_table.addresses)} locations")
            print(f"- {len(self.package_loader.packages)} packages")
            return True
        
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def get_package_status(self, package_id: int, current_time: datetime) -> str:
        """
        Get the status of a package at a specific time.
        Args:
            package_id: ID of the package to get status for
            current_time: Current time to check status at
        Returns:
            Status of the package at the given time
        """
        # First get the package
        package = self.package_loader.get_package(package_id)
        if not package:
            return f"Package {package_id} not found"
        
        # check status based on time
        if package.delivery_time and package.delivery_time <= current_time:
            return f"Delivered at {package.delivery_time.strftime('%I:%M %p')}"
        
        if package.departure_time and package.departure_time <= current_time:
            return f"En Route (departed {package.departure_time.strftime('%I:%M %p')})"
        
        return "At Hub"
    

    def assign_packages_to_trucks(self) -> None:
        """Main method to assign packages to trucks"""
        # 1. First short packages to priority groups   
        groups = self.sort_packages_by_priority()
        
        # 2. then assign groups to trucks
        self.assign_priority_groups(groups)


    def sort_packages_by_priority(self) -> dict:
        """Sort packages by priority groups"""
        groups = {
            'early': [], # 9 AM deadlines
            'morning': [], # 10:30 AM deadlines
            'truck2': [],   # Must be on truck 2
            'delayed': [], # Arrive after 9:05 AM
            'grouped': {}, # Must be delievered togther
            'eod': [], # End of day packages
        }
        
        # get all packages
        packages = self.package_loader.get_all_packages()

        # sort each package
        for package in packages:
            # step 1: check truck restrictions
            if package.required_truck == 2:
                groups['truck2'].append(package)
                continue # skip to next package

            # step 2: check if package is part of a group
            if package.grouped_with:
                # Use smallest ID including current package
                group_id = min(package.grouped_with + [package.package_id])

                if group_id not in groups['grouped']:
                    groups['grouped'][group_id] = []
                groups['grouped'][group_id].append(package)
                 # Also add to delayed if needed
                if package.delayed_until:
                    groups['delayed'].append(package)
                continue

            # step 3: check deadlines
            if package.deadline == time(9, 0):
                groups['early'].append(package)
            elif package.deadline == time(10, 30):
                groups['morning'].append(package)
            else:
                groups['eod'].append(package)

            # step 4: mark if delayed
            if package.delayed_until:
                groups['delayed'].append(package)

        # Print Summary
        print("\nPackage Groups:")
        print(f"Early (9 AM): {len(groups['early'])}")
        print(f"Morning (10:30 AM): {len(groups['morning'])}")
        print(f"Truck 2 Required: {len(groups['truck2'])}")
        print(f"Delayed Packages: {len(groups['delayed'])}")
        print(f"Grouped Packages: {len(groups['grouped'])} groups")
        print(f"EOD Packages: {len(groups['eod'])}")
        
        return groups

    def assign_priority_groups(self, groups: dict) -> None:
        """
        Assign sorted groups to trucks based on priorities:
        """
        # Set truck 3 start time for delayed packages
        delayed_start = datetime(2024, 1, 1, 9, 5)
        self.trucks[2].current_time = delayed_start

        # 1. Handle early deadlines first (9 AM)
        print("\nAssigning early deadline packages:")
        for package in groups['early']:
            if package not in groups['delayed']:  # Skip if delayed
                if len(self.trucks[0].packages) < self.trucks[0].MAX_CAPACITY:
                    self.trucks[0].load_package(package)
                    print(f"Loaded early package {package.package_id} on Truck 1")

        # 2. Handle morning deadlines (10:30 AM)
        print("\nAssigning morning deadline packages:")
        for package in groups['morning']:
            if package not in groups['delayed']:  # Skip if delayed
                # Try truck 1 first
                if len(self.trucks[0].packages) < self.trucks[0].MAX_CAPACITY:
                    success = self.trucks[0].load_package(package)
                    print(f"Loading package {package.package_id} on Truck 1: {'Success' if success else 'Failed'}")
                # Try truck 2 if truck 1 is full
                elif len(self.trucks[1].packages) < self.trucks[1].MAX_CAPACITY:
                    success = self.trucks[1].load_package(package)
                    print(f"Loading package {package.package_id} on Truck 2: {'Success' if success else 'Failed'}")

        # 3. Handle truck 2 requirements
        print("\nAssigning Truck 2 required packages:")
        for package in groups['truck2']:
            if len(self.trucks[1].packages) < self.trucks[1].MAX_CAPACITY:
                success = self.trucks[1].load_package(package)
                if success:
                    print(f"Loaded package {package.package_id} on Truck 2")
                else:
                    print(f"Failed to load package {package.package_id}")

        # 4. Handle delayed packages (must go on truck 3)
        print("\nAssigning delayed packages:")
        for package in groups['delayed']:
            if len(self.trucks[2].packages) < self.trucks[2].MAX_CAPACITY:
                success = self.trucks[2].load_package(package)
                if success:
                    print(f"Loaded delayed package {package.package_id} on Truck 3")
                else:
                    print(f"Failed to load delayed package {package.package_id}")

        # 5. Handle grouped packages
        print("\nAssigning grouped packages:")
        for group_id, group_packages in groups['grouped'].items():
            # Find best truck for group
            best_truck = None
            for truck in self.trucks:
                # Skip if not enough space
                if len(truck.packages) + len(group_packages) > truck.MAX_CAPACITY:
                    continue
                    
                # Check if any package requires truck 2
                requires_truck2 = any(p.required_truck == 2 for p in group_packages)
                if requires_truck2 and truck.truck_id != 2:
                    continue
                    
                # Check if any package is delayed
                has_delayed = any(p.delayed_until for p in group_packages)
                if has_delayed and truck.truck_id != 3:
                    continue
                    
                # Found valid truck
                best_truck = truck
                break
                
            # Load group if we found a valid truck
            if best_truck:
                print(f"Loading group {group_id} on Truck {best_truck.truck_id}")
                for package in group_packages:
                    best_truck.load_package(package)
            else:
                print(f"ERROR: Could not find truck for group {group_id}")

        # 6. Fill remaining space with EOD packages
        print("\nAssigning EOD packages:")
        for package in groups['eod']:
            # Skip if already assigned
            if any(package in truck.packages for truck in self.trucks):
                continue
                
            # Try each truck
            assigned = False
            for truck in self.trucks:
                # Skip if truck full
                if len(truck.packages) >= truck.MAX_CAPACITY:
                    continue
                    
                # Skip if wrong truck
                if package.required_truck == 2 and truck.truck_id != 2:
                    continue
                    
                # Skip if delayed package on wrong truck
                if package.delayed_until and truck.truck_id != 3:
                    continue
                    
                # Load package
                success = truck.load_package(package)
                if success:
                    print(f"Loaded EOD package {package.package_id} on Truck {truck.truck_id}")
                    assigned = True
                    break
                    
            if not assigned:
                print(f"WARNING: Could not assign EOD package {package.package_id}")

        # Print final summary
        print("\nFinal truck loads:")
        for truck in self.trucks:
            print(f"Truck {truck.truck_id}: {len(truck.packages)} packages")

    def run_delivery_routes(self) -> None:
        """
        Run all truck delivery routes using nearest neighbor algorithm
        """
        # First assign packages
        self.assign_packages_to_trucks()

        # run routes for each truck
        print("\nStarting deliveries:")
        for truck in self.trucks:
            if len(truck.packages) > 0:
                print(f"\nRunning route for Truck {truck.truck_id}:")
                print(f"Starting packages {len(truck.packages)}")

                # run this trucks route
                self.run_truck_route(truck)

                # add to total mileage
                self.total_mileage += truck.mileage

        print(f"\nDeliveries complete!")
        print(f"Total mileage: {self.total_mileage:.1f} miles")

    def run_truck_route(self, truck: Truck) -> None:
        """Run delivery route for a single truck"""
        print(f"\nStarting route for Truck {truck.truck_id}")
        print(f"Start time: {truck.current_time.strftime('%I:%M %p')}")

        # Keep track of delivery attempts
        max_attempts = 100  
        attempts = 0

        while len([p for p in truck.packages if p.status != "Delivered"]) > 0:
            attempts += 1
            if attempts > max_attempts:
                print(f"WARNING: Max attempts reached for truck {truck.truck_id}")
                break
            
            # Find next deliverable package
            next_package = None
            shortest_distance = float('inf')
            
            for package in truck.packages:
                if package.status != "Delivered":
                    # Skip if before truck start time
                    if truck.truck_id == 3 and truck.current_time < datetime(2024, 1, 1, 9, 5):
                        continue
                        
                    # Skip if package is delayed
                    if package.delayed_until and truck.current_time.time() < package.delayed_until:
                        continue
                        
                    # Skip wrong address packages before 10:20
                    if package.wrong_address and truck.current_time < datetime(2024, 1, 1, 10, 20):
                        continue
                        
                    # Update wrong address at 10:20
                    if package.wrong_address and truck.current_time >= datetime(2024, 1, 1, 10, 20):
                        package.update_address("410 S State St", truck.current_time)
                    
                    try:
                        distance = self.distance_table.get_distance(
                            truck.current_address,
                            package.address
                        )
                        
                        if distance < shortest_distance:
                            next_package = package
                            shortest_distance = distance
                    except Exception as e:
                        print(f"Error getting distance: {str(e)}")
                        continue
            
            # If no package can be delivered now, wait 5 minutes
            if not next_package:
                truck.current_time += timedelta(minutes=5)
                continue
                
            # Deliver the package
            travel_time = shortest_distance / truck.SPEED
            delivery_time = truck.current_time + timedelta(hours=travel_time)
            
            truck.mileage += shortest_distance
            truck.current_address = next_package.address
            truck.current_time = delivery_time
            next_package.mark_delivered(delivery_time)
            
            print(f"Delivered package {next_package.package_id}")
            print(f"At: {delivery_time.strftime('%I:%M %p')}")
            print(f"Location: {next_package.address}")

        # Return to hub
        if truck.current_address != "Western Governors University":
            try:
                distance = self.distance_table.get_distance(
                    truck.current_address,
                    "Western Governors University"
                )
                truck.mileage += distance
                travel_time = distance / truck.SPEED
                truck.current_time += timedelta(hours=travel_time)
                truck.current_address = "Western Governors University"
            except Exception as e:
                print(f"Error returning to hub: {str(e)}")

        print(f"\nTruck {truck.truck_id} route complete:")
        print(f"End time: {truck.current_time.strftime('%I:%M %p')}")
        print(f"Total mileage: {truck.mileage:.1f}")

    def find_nearest_package(self, truck: Truck) -> Optional[Package]:
        """
        Find nearest undelivered package on truck.
        Returns None if no packages left to deliver.
        """
        nearest_package = None
        shortest_distance = float('inf')

        # check each package on truck
        for package in truck.packages:
            if package.status != "Delivered":
                # get disteance to this package
                distance = self.distance_table.get_distance(
                    truck.current_address,
                    package.address
                )

                # if this is closer than current nearest
                if distance < shortest_distance:
                    # check if we can deliver it now
                    if package.can_be_loaded(truck.current_time, truck.truck_id):
                        nearest_package = package
                        shortest_distance = distance
    
        return nearest_package