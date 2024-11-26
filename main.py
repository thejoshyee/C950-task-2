# Student ID: 012285102

from models.package import Package
from models.hash_table import HashTable

def test_hash_table():
    # create has table
    hash_table = HashTable()

    # create package
    test_package = Package(
        package_id=1,
        address="195 W Oakland Ave",
        deadline="10:30 AM",
        city="Salt Lake City",
        zip_code="84115",
        weight="21 kg"
    )

    # test inserting package
    hash_table.insert(test_package.package_id, test_package)
    print(f"Package {test_package.package_id} inserted into hash table")

    # test look up
    found_package = hash_table.lookup(1)
    if found_package:
        print(f"Found package {found_package.package_id}:")
        print(f"Address: {found_package.address}")
        print(f"Deadline: {found_package.deadline}")
    else:
        print(f"Package not found in hash table")

if __name__ == "__main__":
    test_hash_table()