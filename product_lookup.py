"""
product_lookup.py
--------------------
This file talks to OpenFoodFacts (a free, public, real-world product
database) so we can pull in real product details - name, brand,
ingredients - just by giving a barcode number or typing a product name.

Nothing in here touches our own storeroom (stockpile_store.py). This
file's only job is: "go ask the internet about this product, and hand
back a tidy dictionary describing what it found."
"""

import requests

BARCODE_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"


def lookup_by_barcode(barcode):
    """Looks up a product using its barcode number."""
    try:
        response = requests.get(BARCODE_URL.format(barcode=barcode), timeout=10)
    except requests.exceptions.RequestException as error:
        return {"error": f"Could not reach OpenFoodFacts: {error}"}

    if response.status_code != 200:
        return {"error": f"OpenFoodFacts returned status {response.status_code}"}

    data = response.json()
    if data.get("status") != 1:
        return {"error": "No product found for that barcode."}

    return _format_product(data["product"], barcode)


def lookup_by_name(name):
    """Looks up a product using its name and returns the closest match."""
    params = {"search_terms": name, "json": 1, "page_size": 1}
    try:
        response = requests.get(SEARCH_URL, params=params, timeout=10)
    except requests.exceptions.RequestException as error:
        return {"error": f"Could not reach OpenFoodFacts: {error}"}

    if response.status_code != 200:
        return {"error": f"OpenFoodFacts returned status {response.status_code}"}

    data = response.json()
    products = data.get("products", [])
    if not products:
        return {"error": "No product found for that name."}

    best_match = products[0]
    return _format_product(best_match, best_match.get("code", ""))


def _format_product(product, barcode):
    """Turns OpenFoodFacts' messy real-world data into the clean shape
    our own inventory items use."""
    return {
        "product_name": product.get("product_name") or "Unknown product",
        "brand": product.get("brands") or "Unknown brand",
        "barcode": barcode,
        "ingredients": product.get("ingredients_text") or "No ingredient info available",
        "price": 0.0,
        "stock_level": 0,
        "source": "openfoodfacts",
    }
