# tests/test_distance_table.py
import unittest
import csv
from src.models.distance_table import DistanceTable

class TestDistanceTable(unittest.TestCase):
    def setUp(self):
        self.distance_table = DistanceTable()
        self.distance_table.load_distance_data("src/data/distances.csv")
    
    def test_distance_lookup(self):
        """Test looking up distances between addresses"""
        # Test 1: Distance TO WGU (first column)
        oakland = "South Salt Lake Public Works"
        hub = "Western Governors University"
        distance = self.distance_table.get_distance(oakland, hub)
        self.assertEqual(distance, 3.5)
        
        # Test 2: Distance between two non-WGU locations
        distance = self.distance_table.get_distance(
            "Columbus Library",
            "South Salt Lake Public Works"
        )
        self.assertEqual(distance, 1.5)
        
        # Test 3: Another TO WGU distance
        distance = self.distance_table.get_distance(
            "Sugar House Park",
            "Western Governors University"
        )
        self.assertEqual(distance, 3.8)
        
        # Test 4: Another location pair
        distance = self.distance_table.get_distance(
            "Columbus Library",
            "Deker Lake"
        )
        self.assertEqual(distance, 9.3)
        
        # Test 5: Invalid address should return 0.0
        distance = self.distance_table.get_distance(
            "Invalid Address",
            "Western Governors University"
        )
        self.assertEqual(distance, 0.0)
        
        # Test 6: Both addresses invalid
        distance = self.distance_table.get_distance(
            "Invalid Address 1",
            "Invalid Address 2"
        )
        self.assertEqual(distance, 0.0)

if __name__ == '__main__':
    unittest.main()