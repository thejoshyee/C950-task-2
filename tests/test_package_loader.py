import unittest
from datetime import datetime, time
from src.models.package_loader import PackageLoader
from src.models.package import Package

class TestPackageLoader(unittest.TestCase):
    def setUp(self):
        self.loader = PackageLoader()
        self.loader.load_packages("src/data/packages.csv")
    
    def test_basic_package_loading(self):
        """Test basic package data is loaded correctly"""
        # Get package 1 (Oakland Ave)
        package = self.loader.get_package(1)
        self.assertIsNotNone(package)
        self.assertEqual(package.address, "195 W Oakland Ave")
        self.assertEqual(package.deadline, time(10, 30))  # 10:30 AM
        self.assertEqual(package.status, "At Hub")
    
    def test_delayed_package(self):
        """Test delayed package handling"""
        # Package 6 is delayed until 9:05
        package = self.loader.get_package(6)
        self.assertEqual(package.delayed_until, time(9, 5))
        
        # Shouldn't be available before 9:05
        early_time = datetime(2024, 1, 1, 8, 0)  # 8:00 AM
        self.assertFalse(package.can_be_loaded(early_time, 1))
        
        # Should be available after 9:05
        later_time = datetime(2024, 1, 1, 9, 30)  # 9:30 AM
        self.assertTrue(package.can_be_loaded(later_time, 1))
    
    def test_truck_restriction(self):
        """Test truck restriction handling"""
        # Package 3 can only be on truck 2
        package = self.loader.get_package(3)
        self.assertEqual(package.required_truck, 2)
        
        # Should only load on truck 2
        current_time = datetime(2024, 1, 1, 8, 0)
        self.assertFalse(package.can_be_loaded(current_time, 1))
        self.assertTrue(package.can_be_loaded(current_time, 2))
    
    def test_grouped_packages(self):
        """Test package grouping"""
        # Package 14 must be delivered with 15, 19
        package = self.loader.get_package(14)
        self.assertIn(15, package.grouped_with)
        self.assertIn(19, package.grouped_with)
    
    def test_wrong_address(self):
        """Test wrong address handling"""
        # Package 9 has wrong address
        package = self.loader.get_package(9)
        self.assertTrue(package.wrong_address)
        
        # Address can't be updated before 10:20
        early_time = datetime(2024, 1, 1, 10, 0)
        package.update_address("New Address", early_time)
        self.assertEqual(package.address, "300 State St")  # Original address
        
        # Address can be updated after 10:20
        later_time = datetime(2024, 1, 1, 10, 30)
        package.update_address("410 S State St", later_time)
        self.assertEqual(package.address, "410 S State St")

    def test_special_notes_handling(self):
        """Test that special notes are handled correctly"""
        # Create package with truck 2 requirement
        package = Package(
            package_id=3,
            address="233 Canyon Rd",
            deadline="EOD",
            city="Salt Lake City",
            zip_code="84103",
            weight="2"
        )
        package.required_truck = 2
        
        # Create package that's delayed
        delayed_package = Package(
            package_id=6,
            address="3060 Lester St",
            deadline="10:30 AM",
            city="West Valley City",
            zip_code="84119",
            weight="88"
        )
        delayed_package.delayed_until = time(9, 5)
        
        # Create grouped packages
        group_package = Package(
            package_id=14,
            address="4300 S 1300 E",
            deadline="10:30 AM",
            city="Millcreek",
            zip_code="84117",
            weight="88"
        )
        group_package.grouped_with = [15, 19]

if __name__ == '__main__':
    unittest.main()