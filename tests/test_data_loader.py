# tests/test_data_loader.py
import unittest
from src.models.data_loader import DataLoader
from src.models.hash_table import HashTable


class TestDataLoader(unittest.TestCase):
    def setUp(self):
        """Create a fresh hash table before each test"""
        self.hash_table = HashTable()
        self.csv_path = "src/data/packages.csv" 
    
    def test_load_package_data(self):
        """Test loading package data from CSV"""
        # Load the data
        DataLoader.load_package_data(self.csv_path, self.hash_table)
        
        # Test package 1
        package1 = self.hash_table.lookup(1)
        self.assertIsNotNone(package1, "Package 1 should be loaded")
        self.assertEqual(package1.address, "195 W Oakland Ave")
        self.assertEqual(package1.deadline, "10:30 AM")
        
        # Test package with special notes (package 9)
        package9 = self.hash_table.lookup(9)
        self.assertIsNotNone(package9, "Package 9 should be loaded")
        self.assertEqual(package9.address, "300 State St")
        
        # Verify total packages
        packages = self.hash_table.get_all_packages()
        self.assertEqual(len(packages), 40, "Should have loaded 40 packages")

if __name__ == '__main__':
    unittest.main()