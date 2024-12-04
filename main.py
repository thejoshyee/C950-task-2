# main.py
# Student ID: 012285102
from datetime import datetime
from src.models.delivery_service import DeliveryService

def get_time_input() -> datetime:
    """Get time input from user"""
    while True:
        try:
            time_str = input("Enter time (HH:MM): ")
            hour, minute = map(int, time_str.split(":"))
            return datetime(2024, 1, 1, hour, minute)
        except ValueError:
            print("Invalid time format. Please enter time in HH:MM format (e.g., 13:30)")

def format_package_info(package, status: str, current_time: datetime) -> str:
    """Format package information for display"""    
    info = [
        f"Status: {status}",
        f"Address: {package.get_current_address(current_time)}",
        f"City: {package.city}",
        f"Zip: {package.get_current_zip(current_time)}",
        f"Weight: {package.weight}",
        f"Deadline: {'EOD' if package.deadline.hour == 17 else package.deadline.strftime('%I:%M %p')}"
    ]
    
    # Add special notes if any
    if package.delayed_until:
        info.append(f"Note: Delayed until {package.delayed_until.strftime('%I:%M %p')}")
    if package.required_truck:
        info.append(f"Note: Must be on truck {package.required_truck}")
    if package.wrong_address:
        if current_time.time() < datetime(2024, 1, 1, 10, 20).time():
            info.append("Note: Wrong address - will be corrected at 10:20 AM")
        else:
            info.append("Note: Address has been corrected")
    if package.grouped_with:
        info.append(f"Note: Must be delivered with package(s) {', '.join(map(str, package.grouped_with))}")
    
    return "\n".join(info)

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
            try:
                package_id = int(input("Enter package ID (1-40): "))
                if package_id < 1 or package_id > 40:
                    print("Invalid package ID. Please enter a number between 1 and 40.")
                    continue
                
                check_time = get_time_input()
                package = service.package_loader.get_package(package_id)
                if not package:
                    print(f"Package {package_id} not found")
                    continue
                
                status = service.get_package_status(package_id, check_time)
                print(f"\nPackage {package_id} at {check_time.strftime('%I:%M %p')}:")
                print(format_package_info(package, status, check_time))
                
            except ValueError:
                print("Invalid input. Please enter a valid package ID.")
        
        elif choice == "2":
            # View all packages
            check_time = get_time_input()
            print(f"\nAll packages at {check_time.strftime('%I:%M %p')}:")
            
            # Group packages by truck
            packages_by_truck = {1: [], 2: [], 3: []}
            unassigned = []
            
            for i in range(1, 41):
                package = service.package_loader.get_package(i)
                if package:
                    status = service.get_package_status(i, check_time)
                    # Find which truck the package is on
                    assigned_truck = None
                    for truck in service.trucks:
                        if package in truck.packages:
                            assigned_truck = truck.truck_id
                            break
                    
                    if assigned_truck:
                        packages_by_truck[assigned_truck].append((package, status))
                    else:
                        unassigned.append((package, status))
            
            # Display packages by truck
            for truck_id in [1, 2, 3]:
                if packages_by_truck[truck_id]:
                    print(f"\n{'=' * 20} Truck {truck_id} {'=' * 20}")
                    for package, status in packages_by_truck[truck_id]:
                        print(f"\nPackage {package.package_id}:")
                        print(format_package_info(package, status, check_time))
                        print("-" * 50)
            
            # Display unassigned packages
            if unassigned:
                print(f"\n{'=' * 20} At Hub {'=' * 20}")
                for package, status in unassigned:
                    print(f"\nPackage {package.package_id}:")
                    print(format_package_info(package, status, check_time))
                    print("-" * 50)

        elif choice == "3":
            # View total mileage
            print(f"\nTotal mileage: {service.total_mileage:.1f} miles")
            print("\nMileage by truck:")
            for truck in service.trucks:
                print(f"Truck {truck.truck_id}: {truck.mileage:.1f} miles")

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please select 1-4.")


if __name__ == "__main__":
    main()
