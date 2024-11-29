from typing import Optional, List, Tuple
from .package import Package

class HashTable:
    """
    A hash table implementation for storing and retrieving packages.
    Uses chaining for collision resolution.
    """
    def __init__(self, capacity: int = 40):
        # Initializes empty table with given capacity
        self.capacity: int = capacity
        self.size: int = 0
        self.table: List[List[Tuple[int, Package]]] = [[] for _ in range(capacity)]

    def _hash(self, key: int) -> int:
        """
        Hashes the given key to a value between 0 and capacity-1.
        """
        return key % self.capacity
    
    def insert(self, package_id: int, package: Package) -> None:
        """
        Insert a package into the hash table using package_id as the key.

        Inserts the following data components:
        - delivery address (package.address)
        - delivery deadline (package.deadline)
        - delivery city (package.city)
        - delivery zip code (package.zip_code)
        - package weight (package.weight)
        - delivery status (package.status: at hub, en route, delivered)
        - delivery time (package.delivery_time if delivered)
    
        Args:
            package_id: The unique ID of the package
            package: The Package object containing all delivery data
        """
        slot = self._hash(package_id)

        # Check if the package_id already exists 
        for i, (key, existing_package) in enumerate(self.table[slot]):
            if key == package_id:
                # Update existing package
                self.table[slot][i] = (package_id, package)
                return
        
        # Add new package with all components
        self.table[slot].append((package_id, package))
        self.size += 1

    def lookup(self, package_id: int) -> Optional[Package]:
        """
        Look up a package by its ID.
        Args:
            package_id: The ID of the package to find
            
        Returns:
            Package object containing:
            - delivery address
            - delivery deadline
            - delivery city
            - delivery zip code
            - package weight
            - delivery status (at hub, en route, delivered)
            - delivery time (if delivered)
        """
        slot = self._hash(package_id)

        # Search through the chain at this slot
        for key, package in self.table[slot]:
            if key == package_id:
                return package  # Returns Package with all required components
        
        return None
    
    def get_all_packages(self) -> List[Package]:
        """
        Get all packages in the hash table.
        Returns:
            List of all Package objects in the hash table
        """
        packages = []
        for bucket in self.table:
            for key, package in bucket:
                packages.append(package)
        return packages
