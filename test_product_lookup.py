"""
test_product_lookup.py
--------------------
Tests for our OpenFoodFacts integration. We use unittest.mock so these
tests run instantly and don't depend on the real internet or the real
OpenFoodFacts website being online.

Run with:
    pytest test_product_lookup.py -v
"""

from unittest.mock import patch, Mock

import requests

import product_lookup


@patch("product_lookup.requests.get")
def test_lookup_by_barcode_success(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar",
        },
    }
    mock_get.return_value = mock_response

    result = product_lookup.lookup_by_barcode("1234567890123")
    assert result["product_name"] == "Organic Almond Milk"
    assert result["brand"] == "Silk"
    assert result["source"] == "openfoodfacts"


@patch("product_lookup.requests.get")
def test_lookup_by_barcode_not_found(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": 0}
    mock_get.return_value = mock_response

    result = product_lookup.lookup_by_barcode("0000000000000")
    assert "error" in result


@patch("product_lookup.requests.get")
def test_lookup_by_name_success(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "products": [{
            "product_name": "Peanut Butter",
            "brands": "Jif",
            "ingredients_text": "Peanuts, sugar, salt",
            "code": "111222333",
        }]
    }
    mock_get.return_value = mock_response

    result = product_lookup.lookup_by_name("peanut butter")
    assert result["product_name"] == "Peanut Butter"
    assert result["barcode"] == "111222333"


@patch("product_lookup.requests.get")
def test_lookup_by_name_not_found(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"products": []}
    mock_get.return_value = mock_response

    result = product_lookup.lookup_by_name("nonexistent thing")
    assert "error" in result


@patch("product_lookup.requests.get")
def test_lookup_network_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("boom")
    result = product_lookup.lookup_by_barcode("123")
    assert "error" in result
