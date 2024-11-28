from datetime import datetime
from typing import List
from distance_table import DistanceTable
from .package_loader import PackageLoader
from .truck import Truck

class DeliveryService:
    """
    Main Service managing the WGUPS delivery system.
    Handles loading data, assigning packages, and running deliveries.
    """

    def __init__(self):
        """
        Initialize delivery service with required components.
        Sets up:
            - Distance table for location lookups
            - Package loadering for managing packages
            - Three trucks starting at 8:00 AM
            - Initial mileage tracking
        """
        # Data Management
        self.distance_table = DistanceTable()
        self.package_loader = PackageLoader()

        # Create trucks (all start at 8:00 AM)
        start_time = datetime(2024, 1, 1, 8, 0)
        self.trucks = [
            Truck(1, start_time),
            Truck(2, start_time),
            Truck(3, start_time)
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
        
        Example:
            # Check where package 1 is at 10:30 AM
            time = datetime(2024, 1, 1, 10, 30)
            status = service.get_package_status(1, time)
            # Might return "Delivered at 10:25 AM"
            # or "En Route (departed 10:00 AM)"
            # or "At Hub"
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
                group_id = min(package.grouped_with) # use the smallest id as key
                if group_id not in groups['grouped']:
                    groups['grouped'][group_id] = []
                groups['grouped'][group_id].append(package)
                continue

            # step 3: check deadlines
            deadline = package.deadline
            if deadline.hour == 9 and deadline.minute == 0:
                groups['early'].append(package)
            elif deadline.hour == 10 and deadline.minute == 30:
                groups['morning'].append(package)
            else:
                groups['eod'].append(package)

            # step 4: mark if delayed
            if package.delayed_until:
                groups['delayed'].append(package)

        # print summary for debugging
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
        1. Early deadlines (9 AM) -> Truck 1
        2. Required truck 2 -> Truck 2
        3. Morning deadlines (10:30 AM) -> Split between 1 & 2
        4. Delayed packages -> Truck 3 (starts at 9:05)
        5. EOD packages -> Fill remaining space
        """

        # 1. handle truck 2 requirements 
        print("\nAssigning Truck 2 required packages:")
        truck2 = self.trucks[1]


        for package in groups['truck2']:
            if len(truck2.packages) >= truck2.MAX_CAPACITY:
                print(f"ERROR: Truck 2 is full! Can't load package {package.package_id}")
                continue
            
            # load package
            success = truck2.load_package(package)
            if success:
                print(f"Loaded package {package.package_id} onto truck 2")
            else:
                print(f"ERROR: Failed to load package {package.package_id} onto truck 2")
        
        print(f"Truck 2 has {len(truck2.packages)} packages")

        # 2. handle early deadlines on truck 1
        for package in groups['early']:
            if len(self.trucks[0].packages) < self.trucks[0].MAX_CAPACITY:
                self.trucks[0].load_package(package)

        # 3. handle grouped packages
        print("\nAssigning grouped packages:")
        for group_id, group_packages in groups['grouped'].items():
            # find best truck for group
            best_truck = None

            # check each truck
            for truck in self.trucks:
                # skip if not enough for whole group
                if len(truck.packages) + len(group_packages) > truck.MAX_CAPACITY:
                    continue

            # check if any package requires truck 2
            requires_truck2 = any(p.required_truck == 2 for p in group_packages)
            if requires_truck2 and truck.truck_id != 2:
                continue

            # check if any package is delayed
            has_delayed = any(p.delayed_until for p in group_packages)
            if has_delayed and truck.truck_id != 3:
                continue

            # found valid truck
            best_truck = truck
            break
        
        # load group if we found a valid truck
        if best_truck:
            print(f"Loading group {group_id} on truck {best_truck.truck_id}")
            for package in group_packages:
                best_truck.load_package(package)
        else:
            print(f"ERROR: Could not find truck for group {group_id}")

        # 4. handle delayed packages on truck 3
        print("\nAssigning delayed packages:")
        truck3 = self.trucks[2] 

        for package in groups['delayed']:
            # skip if already assigned (might be in a group)
            if any(package in truck.packages for truck in self.trucks):
                continue

            # check if truck3 has space
            if len(truck3.packages) + 1 > truck3.MAX_CAPACITY:
                print(f"ERROR: Truck 3 full! Can't load delayed package {package.package_id}")
                continue

            # check if package requries truck 2
            if package.required_truck == 2:
                print(f"WARNING: Delayed package {package.package_id} needs truck 2!")
                continue

            # load on truck 3
            success = truck3.load_package(package)
            if success:
                print(f"Loaded delayed package {package.package_id} on Truck 3")
            else:
                print(f"Failed to load delayed package {package.package_id}")
        
        print(f"\nTruck 3 has {len(truck3.packages)} delayed packages")

        # 5. fill in remaining space with EOD packages
        print("\nAssigning EOD packages:")

        for package in groups['eod']:
            # skip if already assigned (might be in a group)
            if any(package in truck.packages for truck in self.trucks):
                continue

            # try to find best truck
            assigned = False
            for truck in self.trucks:
                # skip if truck is full
                if len(truck.packages) >= truck.MAX_CAPACITY:
                    continue
                
                # skip if package needs truck 2 and this isnt truck 2
                if package.required_truck == 2 and truck.truck_id != 2:
                    continue

                # skip if package is delayed and this isnt truck 3
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


        