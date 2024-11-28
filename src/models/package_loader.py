import csv
from datetime import time
from typing import Dict
from .package import Package 


class PackageLoader:
    def __init__(self):
        # Hash table for O(1) lookups
        self.packages: Dict[int, Package] = {}
    
    def load_packages(self, filename: str) -> None:
        """Load and parse package data"""
        with open(filename, "r") as file:
            csv_reader = csv.reader(file)
            
            # Skip headers
            for _ in range(8):
                next(csv_reader)
            
            # Process each package
            for row in csv_reader:
                if len(row) < 8:
                    continue
                
                # Create basic package
                package = Package(
                    package_id=int(row[0]),
                    address=row[1],
                    deadline=row[5],
                    city=row[2],
                    zip_code=row[4],
                    weight=row[6]
                )
                
                # Handle special notes
                notes = row[7]
                if "Delayed" in notes:
                    package.delayed_until = time(9, 5)
                if "Can only be on truck 2" in notes:
                    package.required_truck = 2
                if "Must be delivered with" in notes:
                    # Extract ALL numbers from note
                    import re
                    numbers = re.findall(r'\d+', notes)
                    package.grouped_with = [int(num) for num in numbers]
                if "Wrong address" in notes:
                    package.wrong_address = True
                
                # Store in hash table
                self.packages[package.package_id] = package

    def get_package(self, package_id: int) -> Package:
        """Get package by ID"""
        return self.packages.get(package_id)
    
    def get_all_packages(self) -> list[Package]:
        """Get all packages"""
        return list(self.packages.values())
        
    def get_available_packages(self, current_time: time, truck_id: int) -> list[Package]:
        """Get packages that can be loaded on truck"""
        return [
            package for package in self.packages.values()
            if package.can_be_loaded(current_time, truck_id)
        ]