import csv
from typing import Optional
from .package import Package
from .hash_table import HashTable

class DataLoader:
    """Handles loading package data from CSV file into hash table"""

    @staticmethod
    def load_package_data(filename: str, hash_table: HashTable) -> None:
        """
        Load package data from CSV file into hash table.
        Args:
            filename: The path to the CSV file containing package data
            hash_table: The HashTable object to load data into
        """
        try:
            with open(filename, "r") as file:
                csv_reader = csv.reader(file)
                # Skip header rows
                for _ in range(8):
                    next(csv_reader)

                # Process package data
                for row in csv_reader:
                    if row[0]: # Skip empty rows
                        package = DataLoader._create_package_from_row(row)
                        hash_table.insert(package.package_id, package)

        except FileNotFoundError:
            print(f"File {filename} not found")
        except Exception as e:
            print(f"Error loading package data: {str(e)}")

    @staticmethod
    def _create_package_from_row(row: list) -> Package:
        """
        Create a Package object from a CSV row.
        Args:
            row: List of values from a CSV row
        Returns:
            Package object with data from the row
        """
        package_id = int(row[0])
        address = row[1]
        city = row[2]
        state = row[3]
        zip_code = row[4]
        deadline = row[5]
        weight = row[6]
        notes = row[7] if len(row) > 7 else None

        return Package(
            package_id=package_id,
            address=address,
            deadline=deadline,
            city=city,
            zip_code=zip_code,
            weight=weight
        )
        
