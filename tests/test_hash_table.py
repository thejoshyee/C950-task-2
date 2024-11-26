import unittest
from models.hash_table import HashTable 
from models.package import Package 

print("__name__ is", __name__)

class TestHashTable(unittest.TestCase):
    def setUp(self):
        """Create a fresh hash table before each test"""
        self.hash_table = HashTable()

    def test_insert_and_lookup(self):
        """Test inserting and looking up a package"""
        # create test package
        test_package = Package(
            package_id=1,
            address="195 W Oakland Ave",
            deadline="10:30 AM",
            city="Salt Lake City",
            zip_code="84115",
            weight="21 kg"
        )

        # insert package
        self.hash_table.insert(test_package.package_id, test_package)

        # look up package
        found_package = self.hash_table.lookup(1)

        # Assert package was found and has correct values
        self.assertIsNotNone(found_package)
        self.assertEqual(found_package.address, "195 W Oakland Ave")
        self.assertEqual(found_package.status, "At Hub")

    def test_lookup_missing_package(self):
        """Test looking up a package that doesn't exist"""
        # try to find the package that doesn't exist
        missing_package = self.hash_table.lookup(999)

        # assert it returns None
        self.assertIsNone(missing_package)

    def test_collision_handling(self):
        """Test that multiple packages can be stored in the same slot"""
        # Create packages that will hash to same slot
        package1 = Package(1, "Address 1", "10:30 AM", "SLC", "84111", "5 lbs")
        package41 = Package(41, "Address 2", "EOD", "SLC", "84111", "10 lbs")  # 41 % 40 = 1
        
        # Insert both packages
        self.hash_table.insert(package1.package_id, package1)
        self.hash_table.insert(package41.package_id, package41)
        
        # Verify both can be retrieved
        found1 = self.hash_table.lookup(1)
        found41 = self.hash_table.lookup(41)
        
        self.assertEqual(found1.address, "Address 1")
        self.assertEqual(found41.address, "Address 2")


    def test_package_status_updates(self):
        """Test package status changes through delivery process"""
        package = Package(1, "Address 1", "10:30 AM", "SLC", "84111", "5 lbs")
        self.hash_table.insert(package.package_id, package)
        
        # Get package and mark en route
        pkg = self.hash_table.lookup(1)
        pkg.mark_en_route("9:00 AM")
        self.assertEqual(pkg.status, "En Route")
        
        # Mark delivered
        pkg.mark_delivered("9:30 AM")
        self.assertEqual(pkg.status, "Delivered")



    
if __name__ == "__main__":
    unittest.main()

