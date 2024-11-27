from typing import Optional, List
from .package import Package

class HashTable:
    """
    A hash table implementation for storing and retrieving packages.
    Uses chaining for collision resolution.
    """
    def __init__(self, capacity: int = 40):
        # Initializs empty table with given capacity
        self.capacity: int = capacity
        self.size: int = 0
        self.table: List[List[Package]] = [[] for _ in range(capacity)]

    def _hash(self, key: int) -> int:
        """
        Hashes the given key to a value between 0 and capacity-1.
        """
        return key % self.capacity
    
    def insert(self, package_id: int, package: Package) -> None:
        """
        Insert a package into the hash table using package_id as the key.
        Args:
            package_id: The unique ID of the package
            package: The Package object to store
        """
        slot = self._hash(package_id)

        # Check if the package_id already exists 
        for i, (key, exisiting_package) in enumerate(self.table[slot]):
            if key == package_id:
                # Update existing package
                self.table[slot][i] = (package_id, package)
                return
        
        #add new package
        self.table[slot].append((package_id, package))
        self.size += 1

    def lookup(self, package_id: int) -> Optional[Package]:
        """
        Look up a package by its ID.
        Args:
            package_id: The ID of the package to find
        Returns:
            Package object if found, None if not found
        """
        slot = self._hash(package_id)

        # Search through the chain at this slot
        for key, package in self.table[slot]:
            if key == package_id:
                return package
        
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
    
    
    
