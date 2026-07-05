"""
test_stockpile_api.py
--------------------
Automated tests for the Flask API routes. Run with:
    pytest test_stockpile_api.py -v
"""

import pytest

import stockpile_store as store
import stockpile_api


@pytest.fixture
def client():
    """Gives each test a clean, empty inventory and a test client that
    can send fake requests to our Flask app without needing a real
    server running."""
    store.reset_store()
    stockpile_api.app.config["TESTING"] = True
    with stockpile_api.app.test_client() as test_client:
        yield test_client
    store.reset_store()


def test_get_empty_stock(client):
    response = client.get("/stock")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_item(client):
    response = client.post(
        "/stock",
        json={"product_name": "Almond Milk", "price": 3.5, "stock_level": 10},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["product_name"] == "Almond Milk"
    assert "id" in data


def test_create_item_missing_name(client):
    response = client.post("/stock", json={"price": 3.5})
    assert response.status_code == 400


def test_get_single_item(client):
    created = client.post("/stock", json={"product_name": "Bread"}).get_json()
    response = client.get(f"/stock/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Bread"


def test_get_single_item_not_found(client):
    response = client.get("/stock/999")
    assert response.status_code == 404


def test_update_item(client):
    created = client.post("/stock", json={"product_name": "Cheese", "price": 5}).get_json()
    response = client.patch(f"/stock/{created['id']}", json={"price": 6.5})
    assert response.status_code == 200
    assert response.get_json()["price"] == 6.5


def test_update_item_not_found(client):
    response = client.patch("/stock/999", json={"price": 1})
    assert response.status_code == 404


def test_delete_item(client):
    created = client.post("/stock", json={"product_name": "Yogurt"}).get_json()
    response = client.delete(f"/stock/{created['id']}")
    assert response.status_code == 200

    get_response = client.get(f"/stock/{created['id']}")
    assert get_response.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/stock/999")
    assert response.status_code == 404


def test_lookup_missing_params(client):
    response = client.get("/stock/lookup")
    assert response.status_code == 400
