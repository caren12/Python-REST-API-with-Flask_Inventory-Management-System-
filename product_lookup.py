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

# NOTE: OpenFoodFacts retired their old text-search endpoint (cgi/search.pl).
# It now returns errors for everyone, regardless of headers - it's not
# something we can fix on our end. Their new dedicated search service,
# Search-a-licious, replaces it for name-based lookups.
SEARCH_URL = "https://search.openfoodfacts.org/search"

# OpenFoodFacts blocks requests that don't identify themselves with a
# User-Agent header (this cuts down on anonymous scraper traffic). Without
# this, every request gets rejected with a 403 Forbidden, even though
# nothing else is wrong.
HEADERS = {"User-Agent": "StockpileManager/1.0 (school-project@example.com)"}


def lookup_by_barcode(barcode):
    """Looks up a product using its barcode number."""
    try:
        response = requests.get(
            BARCODE_URL.format(barcode=barcode), headers=HEADERS, timeout=10
        )
    except requests.exceptions.RequestException as error:
        return {"error": f"Could not reach OpenFoodFacts: {error}"}

    if response.status_code != 200:
        return {"error": f"OpenFoodFacts returned status {response.status_code}"}

    data = response.json()
    if data.get("status") != 1:
        return {"error": "No product found for that barcode."}

    return _format_product(data["product"], barcode)


def lookup_by_name(name):
    """Looks up a product using its name and returns the closest match,
    using OpenFoodFacts' newer Search-a-licious search service."""
    params = {"q": name, "page_size": 1}
    try:
        response = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=10)
    except requests.exceptions.RequestException as error:
        return {"error": f"Could not reach OpenFoodFacts: {error}"}

    if response.status_code != 200:
        return {"error": f"OpenFoodFacts returned status {response.status_code}"}

    data = response.json()
    hits = data.get("hits", [])
    if not hits:
        return {"error": "No product found for that name."}

    best_match = hits[0]
    barcode = best_match.get("code") or best_match.get("_id", "")
    return _format_product(best_match, barcode)


def _format_product(product, barcode):
    """Turns OpenFoodFacts' messy real-world data into the clean shape
    our own inventory items use.

    Different OpenFoodFacts endpoints shape their data slightly
    differently - for example, the barcode API gives 'brands' as a
    plain string ("Silk"), but the newer search API gives it as a list
    (["Silk"]). This function handles both cases so the rest of our
    app never has to worry about it.
    """
    return {
        "product_name": product.get("product_name") or "Unknown product",
        "brand": _as_display_text(product.get("brands")) or "Unknown brand",
        "barcode": barcode,
        "ingredients": _get_ingredients_text(product),
        "price": 0.0,
        "stock_level": 0,
        "source": "openfoodfacts",
    }


def _as_display_text(value):
    """Turns a value that might be a string OR a list of strings into
    one readable string, e.g. ["Silk", "Danone"] -> "Silk, Danone"."""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return value


def _get_ingredients_text(product):
    """Gets a human-readable ingredients description. Prefers the
    plain-English 'ingredients_text' field, but some search results
    only include 'ingredients_tags' (coded values like 'en:sugar'), so
    we fall back to cleaning those up into readable words."""
    text = product.get("ingredients_text")
    if text:
        return text

    tags = product.get("ingredients_tags")
    if tags:
        cleaned = [tag.split(":", 1)[-1].replace("-", " ") for tag in tags]
        return ", ".join(cleaned)

    return "No ingredient info available"