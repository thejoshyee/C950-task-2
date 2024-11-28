# tests/test_truck.py
import unittest
from datetime import datetime
from src.models.truck import Truck
from src.models.package import Package
from src.models.distance_table import DistanceTable

class TestTruck(unittest.TestCase):
    def setUp(self):
        # Create distance table
        self.distance_table = DistanceTable()
        self.distance_table.load_distance_data("src/data/distances.csv")
        
        # Create truck starting at 8:00 AM
        self.truck = Truck(1, datetime(2024, 1, 1, 8, 0))
        
        # Create test packages with EXACT addresses from distance table
        self.package1 = Package(
            package_id=1,
            address="South Salt Lake Public Works",  # Changed to Oakland Ave
            deadline="10:30 AM",
            city="Salt Lake City",
            zip_code="84115",
            weight="10"
        )
        self.package2 = Package(
            package_id=2,
            address="Sugar House Park",
            deadline="EOD",
            city="Salt Lake City",
            zip_code="84106",
            weight="15"
        )
    
    def test_load_package(self):
        """Test loading packages onto truck"""
        self.assertTrue(self.truck.load_package(self.package1))
        self.assertEqual(len(self.truck.packages), 1)
        self.assertEqual(self.package1.status, "En Route")
    
    def test_find_nearest_package(self):
        """Test finding nearest undelivered package"""
        self.truck.load_package(self.package1)
        self.truck.load_package(self.package2)
        nearest = self.truck.find_nearest_package(self.distance_table)
        self.assertIsNotNone(nearest)  # Should find a package
    
    def test_deliver_package(self):
        """Test delivering a package"""
        # Load and deliver package to Oakland Ave (known distance: 3.5 miles)
        self.truck.load_package(self.package1)
        
        print("\nTesting distance directly:")
        distance = self.distance_table.get_distance(
            "Western Governors University",
            "South Salt Lake Public Works"
        )
        print(f"Direct distance lookup: {distance} miles")
        
        print("\nDelivering package:")
        self.truck.deliver_package(self.package1, self.distance_table)
        
        print(f"\nFinal state:")
        print(f"Truck mileage: {self.truck.mileage}")
        print(f"Package status: {self.package1.status}")
        print(f"Truck location: {self.truck.current_address}")
        
        # Package should be delivered
        self.assertEqual(self.package1.status, "Delivered")
        # Truck should have moved 3.5 miles
        self.assertEqual(self.truck.mileage, 3.5)
        
    def test_run_delivery_route(self):
        """Test running complete delivery route"""
        self.truck.load_package(self.package1)
        self.truck.load_package(self.package2)
        
        # Run route
        self.truck.run_delivery_route(self.distance_table)
        
        # All packages should be delivered
        self.assertEqual(self.package1.status, "Delivered")
        self.assertEqual(self.package2.status, "Delivered")
        
        # Truck should be back at hub
        self.assertEqual(self.truck.current_address, self.truck.HUB_ADDRESS)
        self.assertEqual(self.truck.status, self.truck.STATUS_AT_HUB)
        # Should have driven some distance
        self.assertGreater(self.truck.mileage, 0.0)

if __name__ == '__main__':
    unittest.main()