
from flask import Flask, jsonify, request

import stockpile_store as store
import product_lookup

app = Flask(__name__)


# Core CRUD routes 

@app.route("/stock", methods=["GET"])
def get_all_stock():
    """Returns the entire inventory list."""
    return jsonify(store.get_all_items()), 200


@app.route("/stock/<int:item_id>", methods=["GET"])
def get_single_stock(item_id):
    """Returns one inventory item by its ID."""
    item = store.get_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/stock", methods=["POST"])
def create_stock():
    """Adds a brand new item to inventory. Requires at least a product_name."""
    data = request.get_json(silent=True)
    if not data or "product_name" not in data:
        return jsonify({"error": "product_name is required"}), 400
    new_item = store.add_item(data)
    return jsonify(new_item), 201


@app.route("/stock/<int:item_id>", methods=["PATCH"])
def update_stock(item_id):
    """Updates one or more fields (like price or stock_level) on an item."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No update data provided"}), 400
    updated = store.update_item(item_id, data)
    if updated is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(updated), 200


@app.route("/stock/<int:item_id>", methods=["DELETE"])
def delete_stock(item_id):
    """Removes an item from inventory permanently."""
    deleted = store.delete_item(item_id)
    if not deleted:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"message": f"Item {item_id} deleted"}), 200


# Helper routes - these use the external OpenFoodFacts API

@app.route("/stock/lookup", methods=["GET"])
def lookup_product():
    """Looks up product info online without saving it to inventory.
    Usage: /stock/lookup?barcode=1234567890123
       or: /stock/lookup?name=almond milk
    """
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if barcode:
        result = product_lookup.lookup_by_barcode(barcode)
    elif name:
        result = product_lookup.lookup_by_name(name)
    else:
        return jsonify({"error": "Provide a 'barcode' or 'name' query parameter"}), 400

    if "error" in result:
        return jsonify(result), 404
    return jsonify(result), 200


@app.route("/stock/lookup/add", methods=["POST"])
def lookup_and_add_product():
    """Looks up a product online AND immediately adds it to inventory.
    Send JSON body like: {"barcode": "1234567890123", "price": 3.5, "stock_level": 10}
    """
    data = request.get_json(silent=True) or {}
    barcode = data.get("barcode")
    name = data.get("name")

    if barcode:
        result = product_lookup.lookup_by_barcode(barcode)
    elif name:
        result = product_lookup.lookup_by_name(name)
    else:
        return jsonify({"error": "Provide 'barcode' or 'name' in the request body"}), 400

    if "error" in result:
        return jsonify(result), 404

    # Let the caller set their own price/stock instead of the API defaults
    if "price" in data:
        result["price"] = data["price"]
    if "stock_level" in data:
        result["stock_level"] = data["stock_level"]

    new_item = store.add_item(result)
    return jsonify(new_item), 201


if __name__ == "__main__":
    app.run(debug=True)
