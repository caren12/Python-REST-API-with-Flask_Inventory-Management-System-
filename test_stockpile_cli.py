"""
test_stockpile_cli.py
--------------------
Tests for the CLI tool. We fake ("mock") both the user's keyboard input
and the network requests, so these tests run instantly without needing
a real server or a real person typing anything.

Run with:
    pytest test_stockpile_cli.py -v
"""

from unittest.mock import patch, Mock

import stockpile_cli


@patch("stockpile_cli.requests.get")
def test_view_all_items_prints_items(mock_get, capsys):
    mock_response = Mock()
    mock_response.json.return_value = [
        {"id": 1, "product_name": "Milk", "brand": "Silk", "price": 3.0, "stock_level": 5}
    ]
    mock_get.return_value = mock_response

    stockpile_cli.view_all_items()
    captured = capsys.readouterr()
    assert "Milk" in captured.out


@patch("stockpile_cli.requests.get")
def test_view_all_items_empty(mock_get, capsys):
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    stockpile_cli.view_all_items()
    captured = capsys.readouterr()
    assert "empty" in captured.out.lower()


@patch("stockpile_cli.requests.post")
@patch("builtins.input", side_effect=["Bread", "Wonder", "2.5", "20"])
def test_add_item_manually(mock_input, mock_post, capsys):
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 1, "product_name": "Bread"}
    mock_post.return_value = mock_response

    stockpile_cli.add_item_manually()
    captured = capsys.readouterr()
    assert "Item added" in captured.out


@patch("builtins.input", side_effect=["Bread", "Wonder", "notanumber", "20"])
def test_add_item_manually_bad_price(mock_input, capsys):
    stockpile_cli.add_item_manually()
    captured = capsys.readouterr()
    assert "must be numbers" in captured.out


@patch("stockpile_cli.requests.delete")
@patch("builtins.input", side_effect=["3"])
def test_delete_item(mock_input, mock_delete, capsys):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "Item 3 deleted"}
    mock_delete.return_value = mock_response

    stockpile_cli.delete_item()
    captured = capsys.readouterr()
    assert "deleted" in captured.out


@patch("stockpile_cli.requests.get")
@patch("builtins.input", side_effect=["999"])
def test_view_one_item_not_found(mock_input, mock_get, capsys):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    stockpile_cli.view_one_item()
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()
