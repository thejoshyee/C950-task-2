import csv
from typing import List

class DistanceTable:
    """
    Handles loading and retrieving distances between locations.
    CSV Format:
    - Column 0: Location name and address
    - Column 1: Address and zip (not used)
    - Column 2: Distance to WGU
    - Column 3+: Distances to other locations
    """

    def __init__(self):
        # Store addresses from header row (skipping first two columns)
        self.addresses: List[str] = []
        # Store raw CSV rows for direct distance lookups
        self.raw_rows: List[List[str]] = []

    def load_distance_data(self, filename: str) -> None:
        """
        Load distance data from CSV file
        Args:
            filename: Path to distance data CSV
        """
        try:
            with open(filename, "r") as file:
                csv_reader = csv.reader(file)
                
                # Skip first 8 rows (headers)
                for _ in range(8):
                    next(csv_reader)
                
                # Get addresses from header row (skip first two columns)
                header = next(csv_reader)
                self.addresses = [addr.strip() for addr in header[2:] if addr.strip()]
                
                # Skip empty row and HUB row
                next(csv_reader)
                next(csv_reader)
                
                # Store each valid row (must have at least name and one distance)
                self.raw_rows = []
                for row in csv_reader:
                    if len(row) >= 3:  # Name, zip, and at least one distance
                        self.raw_rows.append(row)

        except FileNotFoundError:
            print(f"Error: File {filename} not found")
        except Exception as e:
            print(f"Error loading distances: {str(e)}")


    def get_distance(self, address1: str, address2: str) -> float:
        """Get distance between two addresses"""
        try:
            print(f"\nLooking up distance from {address1} to {address2}")
            
            # Find the row containing address1
            source_row = None
            for row in self.raw_rows:
                if address1 in row[0]:
                    source_row = row
                    print(f"Found source row: {row}")
                    break
                    
            # If we didn't find the source address
            if not source_row:
                # Check if it's WGU (it won't be in raw_rows)
                if "Western Governors University" in address1:
                    # Find destination row and get its WGU distance
                    for row in self.raw_rows:
                        if address2 in row[0]:
                            distance = float(row[2])  # Distance TO WGU
                            print(f"Found WGU distance: {distance}")
                            return distance
                return 0.0
                
            # If going TO WGU, use column 2
            if "Western Governors University" in address2:
                distance = float(source_row[2])
                print(f"Distance to WGU: {distance}")
                return distance
                
            # For other addresses, find column index
            for i, addr in enumerate(self.addresses):
                if address2 in addr:
                    # Add 2 because we skipped first two columns
                    distance = float(source_row[i + 2])
                    print(f"Regular distance: {distance}")
                    return distance
                    
            return 0.0
                
        except Exception as e:
            print(f"Error getting distance: {str(e)}")
            return 0.0