# Student ID: 012285102

from datetime import datetime
from src.models.delivery_service import DeliveryService

def get_time_input() -> datetime:
    """Get time input from user"""
    while True:
        try:
            time_str = input("Enter time (HH:MM): ")
            hour, minute = map(int, time_str.split(":"))
            return datetime(2024, 1,1, hour, minute)
        except ValueError:
            print("Invalid time format. Please enter time in HH:MM format (e.g., 13:30)")


def main():
    # initialize delivery service
    service = DeliveryService()
    service.load_data("src/data/distances.csv", "src/data/packages.csv")

    # run delivery routes
    service.run_delivery_routes()

    while True:
        print("\nWGUPS Package Tracking")
        print("1. Look up package")
        print("2. View all packages")
        print("3. View total mileage")
        print("4. Exit")

        choice = input("\nSelect option (1-4): ")

        if choice == "1":
            # Look up specific package
            package_id = int(input("Enter package ID: "))
            check_time = get_time_input()
            status = service.get_package_status(package_id, check_time)
            print(f"\nPackage {package_id} status at {check_time.strftime('%I:%M %p')}:")
            print(status)
        
        elif choice == "2":
            # View all packages
            check_time = get_time_input()
            print(f"\nAll packages at {check_time.strftime('%I:%M %p')}:")
            for i in range(1, 40):
                status = service.get_package_status(i, check_time)
                print(f"Package {i} status: {status}")

        elif choice == "3":
            # View total mileage
            print(f"\nTotal mileage: {service.total_mileage:.1f} miles")

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please select 1-4.")


if __name__ == "__main__":
    main()