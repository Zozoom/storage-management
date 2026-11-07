import pytest
from fastapi import HTTPException

from app.models import Item
from app.routers.items import adjust_stock, get_item, to_item_out, update_item
from app.schemas import ItemUpdate, StockAdjust


def test_list_items(client, auth_headers):
    response = client.get("/api/items", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["sku"] == "TEST-1"
    assert items[0]["low_stock"] is False


def test_list_items_unauthorized(client):
    response = client.get("/api/items")
    assert response.status_code == 401


def test_create_item(client, auth_headers):
    response = client.post(
        "/api/items",
        headers=auth_headers,
        json={
            "sku": "NEW-1",
            "name": "New Thing",
            "quantity": 5,
            "location": "A-99",
            "min_stock": 2,
        },
    )
    assert response.status_code == 201
    assert response.json()["sku"] == "NEW-1"


def test_adjust_stock(client, auth_headers):
    listed = client.get("/api/items", headers=auth_headers).json()
    item_id = listed[0]["id"]

    response = client.post(
        f"/api/items/{item_id}/adjust",
        headers=auth_headers,
        json={"delta": -3},
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 7


def test_adjust_stock_insufficient(client, auth_headers):
    listed = client.get("/api/items", headers=auth_headers).json()
    item_id = listed[0]["id"]

    response = client.post(
        f"/api/items/{item_id}/adjust",
        headers=auth_headers,
        json={"delta": -999},
    )
    assert response.status_code == 400


def test_delete_item(client, auth_headers):
    listed = client.get("/api/items", headers=auth_headers).json()
    item_id = listed[0]["id"]

    response = client.delete(f"/api/items/{item_id}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get("/api/items", headers=auth_headers).json() == []


def test_low_stock_is_true_only_below_minimum(db_session):
    item = db_session.query(Item).first()
    assert to_item_out(item).low_stock is False

    item.quantity = item.min_stock
    assert to_item_out(item).low_stock is False

    item.quantity = item.min_stock - 1
    assert to_item_out(item).low_stock is True


def test_partial_update_changes_only_supplied_fields_and_missing_item_returns_404(db_session):
    item = db_session.query(Item).first()
    original_quantity = item.quantity

    updated = update_item(item.id, ItemUpdate(name="Renamed"), db_session, None)
    assert updated.name == "Renamed"
    assert updated.quantity == original_quantity

    with pytest.raises(HTTPException) as exc_info:
        get_item(9999, db_session, None)
    assert exc_info.value.status_code == 404


def test_stock_adjustment_updates_quantity_and_rejects_negative_result(db_session):
    item = db_session.query(Item).first()
    adjusted = adjust_stock(item.id, StockAdjust(delta=3), db_session, None)
    assert adjusted.quantity == 13

    with pytest.raises(HTTPException) as exc_info:
        adjust_stock(item.id, StockAdjust(delta=-14), db_session, None)
    assert exc_info.value.status_code == 400
    assert db_session.get(Item, item.id).quantity == 13
