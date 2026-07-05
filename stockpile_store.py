
STOCK = []
_next_id = 1


def _generate_id():
    """Hands out the next unused ID number, like a ticket dispenser."""
    global _next_id
    new_id = _next_id
    _next_id += 1
    return new_id


def get_all_items():
    """Returns every item currently in the storeroom."""
    return STOCK


def get_item(item_id):
    """Finds one item by its ID. Returns None if it doesn't exist."""
    for item in STOCK:
        if item["id"] == item_id:
            return item
    return None


def add_item(data):
    """Creates a new item on the shelf and gives it a fresh ID."""
    new_item = {
        "id": _generate_id(),
        "product_name": data.get("product_name", "Unnamed product"),
        "brand": data.get("brand", "Unknown"),
        "barcode": data.get("barcode", ""),
        "price": data.get("price", 0.0),
        "stock_level": data.get("stock_level", 0),
        "ingredients": data.get("ingredients", ""),
        "source": data.get("source", "manual"),
    }
    STOCK.append(new_item)
    return new_item


def update_item(item_id, data):
    """Changes only the fields that were sent in, leaves the rest alone."""
    item = get_item(item_id)
    if item is None:
        return None

    editable_fields = [
        "product_name", "brand", "barcode",
        "price", "stock_level", "ingredients", "source",
    ]
    for field in editable_fields:
        if field in data:
            item[field] = data[field]
    return item


def delete_item(item_id):
    """Removes an item from the shelf. Returns True/False for success."""
    item = get_item(item_id)
    if item is None:
        return False
    STOCK.remove(item)
    return True


def reset_store():
    """Empties the shelf completely. Only used by our automated tests
    so every test starts from a clean, predictable state."""
    global STOCK, _next_id
    STOCK = []
    _next_id = 1
