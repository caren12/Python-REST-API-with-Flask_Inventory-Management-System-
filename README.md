# Stockpile Manager — Inventory Management System

A simple inventory system built for a small retail shop. It lets staff
add, view, update, and delete products in stock, and can pull in real
product details (name, brand, ingredients) from the free
[OpenFoodFacts](https://openfoodfacts.github.io/openfoodfacts-server/api/)
database using a barcode or product name — no need to type everything
in by hand.


## What's in this project

| File | Plain-English purpose |
|---|---|
| `stockpile_store.py` | The "pretend database" — holds inventory items in memory while the app runs. |
| `product_lookup.py` | Talks to the OpenFoodFacts website to find real product info. |
| `stockpile_api.py` | The Flask web server. This is the "engine" — it must be running for anything else to work. |
| `stockpile_cli.py` | The menu-driven tool staff actually use day-to-day. |
| `test_stockpile_api.py` | Automated tests for the web server's routes. |
| `test_product_lookup.py` | Automated tests for the OpenFoodFacts connection. |
| `test_stockpile_cli.py` | Automated tests for the staff menu tool. |
| `requirements.txt` | List of Python packages this project needs. |

---

## 1. Installation and Setup

You'll need **Python 3.9+** installed.

```bash
# 1. Clone your repo and go into the project folder
git clone <your-repo-url>
cd <your-repo-folder>

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 2. Running the system

You need **two terminal windows** open at the same time.

**Terminal 1 — start the API server (the "engine"):**
```bash
python stockpile_api.py
```
Leave this running. You should see Flask say it's running on
`http://127.0.0.1:5000`.

**Terminal 2 — start the staff menu tool:**
```bash
python stockpile_cli.py
```
You'll see a numbered menu. Type a number and press Enter to use it.

---

## 3. API Endpoints (for developers / Postman)

Base URL: `http://127.0.0.1:5000`

| Method | Route | What it does | Body / Params |
|---|---|---|---|
| GET | `/stock` | List every item in inventory | none |
| GET | `/stock/<id>` | Get one item by ID | none |
| POST | `/stock` | Add a new item manually | JSON: `product_name` (required), `brand`, `price`, `stock_level`, `ingredients`, `barcode` |
| PATCH | `/stock/<id>` | Update one or more fields on an item | JSON: any of `product_name`, `brand`, `price`, `stock_level`, `ingredients`, `barcode` |
| DELETE | `/stock/<id>` | Remove an item | none |
| GET | `/stock/lookup` | Search OpenFoodFacts, don't save | query param `?barcode=...` or `?name=...` |
| POST | `/stock/lookup/add` | Search OpenFoodFacts AND save the result to inventory | JSON: `barcode` or `name`, optionally `price`/`stock_level` to override |

### Example: add an item manually
```bash
curl -X POST http://127.0.0.1:5000/stock \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Organic Almond Milk", "brand": "Silk", "price": 3.99, "stock_level": 25}'
```

### Example: look up a product online and add it straight to inventory
```bash
curl -X POST http://127.0.0.1:5000/stock/lookup/add \
  -H "Content-Type: application/json" \
  -d '{"barcode": "3017620422003", "price": 4.50, "stock_level": 15}'
```

### Example item shape stored in inventory
```json
{
  "id": 1,
  "product_name": "Organic Almond Milk",
  "brand": "Silk",
  "barcode": "3017620422003",
  "price": 3.99,
  "stock_level": 25,
  "ingredients": "Filtered water, almonds, cane sugar",
  "source": "manual"
}
```

---

## 4. Using the CLI (for shop staff)

Once both terminals are running, the CLI shows:

```
===== Stockpile Inventory Manager =====
1. View all items
2. View one item
3. Add a new item manually
4. Update price or stock level
5. Delete an item
6. Look up a product online (OpenFoodFacts)
7. Look up a product online AND add it to inventory
8. Exit
```

Just type the number of what you want to do. For example, to add a
product straight from the internet:
1. Choose `7`
2. Choose `b` for barcode (or `n` to search by name)
3. Type the barcode/name
4. Optionally type a price and stock level (or leave blank)
5. The item appears in your inventory automatically

---

## 5. Testing — how to check everything works

This project has an automated test suite plus a manual "does it
actually work" checklist.

### Automated tests (recommended — run these first)

```bash
pytest -v
```

This runs every test file (`test_stockpile_api.py`,
`test_product_lookup.py`, `test_stockpile_cli.py`) and prints a
pass/fail result for each one. All tests use fake ("mocked") data, so
they run instantly and never need the internet or a running server.

You should see something like:
```
test_stockpile_api.py::test_get_empty_stock PASSED
test_stockpile_api.py::test_create_item PASSED
...
======================== 20 passed in 0.45s =========================
```

### Manual, hands-on testing (to see it work live)

1. **Start the server**: `python stockpile_api.py` — confirm it says
   "Running on http://127.0.0.1:5000".
2. **Check it's alive**: open a browser and go to
   `http://127.0.0.1:5000/stock` — you should see an empty list `[]`.
3. **Add an item through the CLI**: run `python stockpile_cli.py`,
   choose option `3`, and fill in a name/brand/price/stock level.
4. **Confirm it saved**: refresh `http://127.0.0.1:5000/stock` in your
   browser, or choose option `1` in the CLI — your new item should
   appear.
5. **Try the external lookup**: in the CLI, choose option `6`, search
   by name (e.g. "nutella"), and confirm real product data comes back
   from OpenFoodFacts.
6. **Update it**: choose option `4`, enter the item's ID, and change
   the price or stock level. Recheck with option `1`.
7. **Delete it**: choose option `5`, enter the ID, and confirm it's
   gone by choosing option `1` again.
8. **Test error handling**: try viewing/updating/deleting an ID that
   doesn't exist (e.g. `999`) — you should get a friendly "not found"
   message instead of a crash.

If you have [Postman](https://www.postman.com/), you can also import
the routes from section 3 above and test each one directly — this is a
good way to double-check the API independently of the CLI.

---

## 6. Git workflow used for this project

To keep history clean, this project was built using feature branches,
merged back into `main` through pull requests:

- `feature/inventory-crud-routes` — Flask CRUD routes
- `feature/external-api-lookup` — OpenFoodFacts integration
- `feature/cli-tool` — the staff-facing CLI
- `feature/unit-tests` — the pytest test suite

Each branch was merged into `main` via a pull request and deleted
afterward once merged, keeping the branch list tidy.

---

## Notes

- Inventory data lives in memory only (a Python list) — it resets
  every time you restart `stockpile_api.py`. That's intentional for
  this lab; a real production version would swap `stockpile_store.py`
  for a real database.
- OpenFoodFacts is a public, free database — no API key required.
