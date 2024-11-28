import unittest
from datetime import datetime, time
from src.models.delivery_service import DeliveryService

class TestDeliveryService(unittest.TestCase):
    def setUp(self):
        """Set up delivery service with test data"""
        self.service = DeliveryService()
        # Load real data
        self.service.load_data(
            "src/data/distances.csv",
            "src/data/packages.csv"
        )
    
    def test_package_assignment(self):
        """Test that packages are assigned correctly"""
        # Run assignment
        self.service.assign_packages_to_trucks()
        
        # Check truck loads
        for truck in self.service.trucks:
            # Shouldn't exceed capacity
            self.assertLessEqual(
                len(truck.packages), 
                truck.MAX_CAPACITY,
                f"Truck {truck.truck_id} overloaded!"
            )
            
            # Check special requirements
            for package in truck.packages:
                # If requires truck 2, must be on truck 2
                if package.required_truck == 2:
                    self.assertEqual(
                        truck.truck_id, 2,
                        f"Package {package.package_id} on wrong truck!"
                    )
                
                # If delayed, must be on truck 3
                if package.delayed_until:
                    self.assertEqual(
                        truck.truck_id, 3,
                        f"Delayed package {package.package_id} on wrong truck!"
                    )
    
    def test_delivery_route(self):
        """Test complete delivery route"""
        # Run full delivery
        self.service.assign_packages_to_trucks()
        self.service.run_delivery_routes()
        
        # Check all packages delivered
        packages = self.service.package_loader.get_all_packages()
        for package in packages:
            self.assertEqual(
                package.status,
                "Delivered",
                f"Package {package.package_id} not delivered!"
            )
            
            # Check delivery times
            if package.deadline != time(17, 0):  # Not EOD
                self.assertLessEqual(
                    package.delivery_time.time(),
                    package.deadline,
                    f"Package {package.package_id} missed deadline!"
                )
        
        # Check total mileage under 140
        self.assertLess(
            self.service.total_mileage,
            140,
            f"Total mileage {self.service.total_mileage} exceeds 140!"
        )
    
    def test_delivery_timing(self):
        """Test specific delivery timing requirements"""
        self.service.run_delivery_routes()
        
        # Get some packages with specific requirements
        packages = self.service.package_loader.get_all_packages()
        
        # Check delayed package timing
        delayed_packages = [p for p in packages if p.delayed_until]
        for package in delayed_packages:
            self.assertGreaterEqual(
                package.departure_time.time(),
                time(9, 5),
                f"Delayed package {package.package_id} left too early!"
            )
        
        # Check wrong address timing
        wrong_address = next(p for p in packages if p.wrong_address)
        self.assertGreaterEqual(
            wrong_address.delivery_time.time(),
            time(10, 20),
            f"Wrong address package delivered too early!"
        )

if __name__ == '__main__':
    unittest.main()