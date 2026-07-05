import requests

BASE_URL = "http://127.0.0.1:5000"


def show_menu():
    print("\n===== Stockpile Inventory Manager =====")
    print("1. View all items")
    print("2. View one item")
    print("3. Add a new item manually")
    print("4. Update price or stock level")
    print("5. Delete an item")
    print("6. Look up a product online (OpenFoodFacts)")
    print("7. Look up a product online AND add it to inventory")
    print("8. Exit")


def view_all_items():
    response = requests.get(f"{BASE_URL}/stock")
    items = response.json()
    if not items:
        print("Inventory is empty.")
        return
    for item in items:
        print(f"[{item['id']}] {item['product_name']} - {item['brand']} "
              f"- ${item['price']} - stock: {item['stock_level']}")


def view_one_item():
    item_id = input("Enter item ID: ").strip()
    response = requests.get(f"{BASE_URL}/stock/{item_id}")
    if response.status_code == 404:
        print("Item not found.")
        return
    print(response.json())


def add_item_manually():
    name = input("Product name: ").strip()
    brand = input("Brand: ").strip()
    try:
        price = float(input("Price: ").strip())
        stock_level = int(input("Stock level: ").strip())
    except ValueError:
        print("Price/stock level must be numbers. Try again.")
        return

    payload = {
        "product_name": name,
        "brand": brand,
        "price": price,
        "stock_level": stock_level,
    }
    response = requests.post(f"{BASE_URL}/stock", json=payload)
    if response.status_code == 201:
        print("Item added:", response.json())
    else:
        print("Error:", response.json())


def update_item():
    item_id = input("Enter item ID to update: ").strip()
    print("Leave a field blank to keep it unchanged.")
    price_input = input("New price: ").strip()
    stock_input = input("New stock level: ").strip()

    payload = {}
    if price_input:
        try:
            payload["price"] = float(price_input)
        except ValueError:
            print("Price must be a number. Cancelled.")
            return
    if stock_input:
        try:
            payload["stock_level"] = int(stock_input)
        except ValueError:
            print("Stock level must be a whole number. Cancelled.")
            return

    if not payload:
        print("Nothing to update.")
        return

    response = requests.patch(f"{BASE_URL}/stock/{item_id}", json=payload)
    if response.status_code == 200:
        print("Item updated:", response.json())
    else:
        print("Error:", response.json())


def delete_item():
    item_id = input("Enter item ID to delete: ").strip()
    response = requests.delete(f"{BASE_URL}/stock/{item_id}")
    if response.status_code == 200:
        print(response.json()["message"])
    else:
        print("Error:", response.json())


def lookup_product(add_to_inventory=False):
    choice = input("Search by (b)arcode or (n)ame? ").strip().lower()
    payload = {}
    if choice == "b":
        payload["barcode"] = input("Enter barcode: ").strip()
    else:
        payload["name"] = input("Enter product name: ").strip()

    if add_to_inventory:
        price_input = input("Price to store (optional, press enter to skip): ").strip()
        stock_input = input("Stock level to store (optional, press enter to skip): ").strip()
        if price_input:
            payload["price"] = float(price_input)
        if stock_input:
            payload["stock_level"] = int(stock_input)
        response = requests.post(f"{BASE_URL}/stock/lookup/add", json=payload)
    else:
        response = requests.get(f"{BASE_URL}/stock/lookup", params=payload)

    if response.status_code in (200, 201):
        print(response.json())
    else:
        print("Error:", response.json())


def main():
    while True:
        show_menu()
        choice = input("Choose an option (1-8): ").strip()
        if choice == "1":
            view_all_items()
        elif choice == "2":
            view_one_item()
        elif choice == "3":
            add_item_manually()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            lookup_product(add_to_inventory=False)
        elif choice == "7":
            lookup_product(add_to_inventory=True)
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Please choose a number between 1 and 8.")


if __name__ == "__main__":
    main()
