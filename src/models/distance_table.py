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
        """
        Get distance between two addresses
        Args:
            address1: Source address
            address2: Destination address
        Returns:
            Distance in miles, or 0.0 if addresses not found
        """
        try:
            # Looking up distance TO WGU
            if address2.strip() == "Western Governors University":
                # Find the source address row
                for row in self.raw_rows:
                    if address1 in row[0]:
                        # Return first distance value (column 2)
                        try:
                            return float(row[2])
                        except (ValueError, IndexError):
                            return 0.0
            
            # For other addresses, find destination column in header
            addr2_index = -1
            for i, addr in enumerate(self.addresses):
                if address2 in addr:
                    addr2_index = i
                    break
            
            if addr2_index != -1:
                # Find source address row
                for row in self.raw_rows:
                    if address1 in row[0]:
                        try:
                            # Add 2 to index because we skipped first two columns
                            return float(row[addr2_index + 2])
                        except (ValueError, IndexError):
                            return 0.0
            
            return 0.0
            
        except Exception as e:
            print(f"Error getting distance: {str(e)}")
            return 0.0