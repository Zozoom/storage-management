import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.main import MAX_REQUEST_BODY_SIZE
from app.models import Item
from app.routers.items import adjust_stock, delete_item, get_item, update_item
from app.schemas import (
    MAX_DESCRIPTION_LENGTH,
    MAX_QUANTITY,
    ItemCreate,
    ItemUpdate,
    StockAdjust,
)


def test_item_create_accepts_valid_field_boundaries():
    item = ItemCreate(
        sku="S" * 64,
        name="N" * 128,
        quantity=0,
        min_stock=0,
    )

    assert len(item.sku) == 64
    assert len(item.name) == 128
    assert item.quantity == 0
    assert item.min_stock == 0


@pytest.mark.parametrize(
    "fields",
    [
        {"sku": "", "name": "Item"},
        {"sku": "S" * 65, "name": "Item"},
        {"sku": "SKU", "name": ""},
        {"sku": "SKU", "name": "N" * 129},
        {"sku": "SKU", "name": "Item", "quantity": -1},
        {"sku": "SKU", "name": "Item", "min_stock": -1},
    ],
)
def test_item_create_rejects_invalid_field_values(fields):
    with pytest.raises(ValidationError):
        ItemCreate(**fields)


def test_item_create_defaults_and_nullable_description():
    item = ItemCreate(sku="SKU", name="Item")
    item_with_null_description = ItemCreate(
        sku="SKU-2", name="Another item", description=None
    )

    assert item.description is None
    assert item.quantity == 0
    assert item.location == "A-01"
    assert item.min_stock == 5
    assert item_with_null_description.description is None


def test_item_update_accepts_omitted_fields_and_rejects_invalid_supplied_values():
    update = ItemUpdate()

    assert update.model_dump(exclude_unset=True) == {}

    for fields in ({"name": ""}, {"quantity": -1}, {"min_stock": -1}):
        with pytest.raises(ValidationError):
            ItemUpdate(**fields)


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


def test_create_item_rejects_out_of_range_fields(client, auth_headers):
    too_long_description = client.post(
        "/api/items",
        headers=auth_headers,
        json={
            "sku": "LONG-DESC",
            "name": "Long description",
            "description": "x" * (MAX_DESCRIPTION_LENGTH + 1),
        },
    )
    assert too_long_description.status_code == 422

    excessive_quantity = client.post(
        "/api/items",
        headers=auth_headers,
        json={
            "sku": "LARGE-QTY",
            "name": "Large quantity",
            "quantity": MAX_QUANTITY + 1,
        },
    )
    assert excessive_quantity.status_code == 422


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


def test_adjust_stock_rejects_quantity_above_limit(client, auth_headers, db_session):
    item = db_session.query(Item).first()
    item.quantity = MAX_QUANTITY
    db_session.commit()

    response = client.post(
        f"/api/items/{item.id}/adjust",
        headers=auth_headers,
        json={"delta": 1},
    )
    assert response.status_code == 422


def test_adjust_stock_rejects_out_of_range_delta(client, auth_headers):
    listed = client.get("/api/items", headers=auth_headers).json()
    item_id = listed[0]["id"]

    response = client.post(
        f"/api/items/{item_id}/adjust",
        headers=auth_headers,
        json={"delta": MAX_QUANTITY + 1},
    )
    assert response.status_code == 422


def test_oversized_request_body_is_rejected(client):
    response = client.post(
        "/api/items",
        content=b"x" * (MAX_REQUEST_BODY_SIZE + 1),
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json()["detail"] == "Request body too large"


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


def test_partial_item_update_preserves_unspecified_fields(db_session):
    item = db_session.query(Item).first()
    original = {
        "sku": item.sku,
        "description": item.description,
        "quantity": item.quantity,
        "location": item.location,
        "min_stock": item.min_stock,
    }

    updated = update_item(item.id, ItemUpdate(name="Updated item"), db_session)

    assert updated.name == "Updated item"
    assert updated.sku == original["sku"]
    assert updated.description == original["description"]
    assert updated.quantity == original["quantity"]
    assert updated.location == original["location"]
    assert updated.min_stock == original["min_stock"]


def test_stock_adjustments_update_quantity_and_low_stock_status(db_session):
    item = db_session.query(Item).first()
    item.quantity = 6
    db_session.commit()

    decreased = adjust_stock(item.id, StockAdjust(delta=-2), db_session)
    assert decreased.quantity == 4
    assert decreased.low_stock is True

    increased = adjust_stock(item.id, StockAdjust(delta=2), db_session)
    assert increased.quantity == 6
    assert increased.low_stock is False


def test_stock_adjustment_rejects_negative_quantity_without_changing_stock(db_session):
    item = db_session.query(Item).first()
    original_quantity = item.quantity

    with pytest.raises(HTTPException) as error:
        adjust_stock(item.id, StockAdjust(delta=-(original_quantity + 1)), db_session)

    assert error.value.status_code == 400
    assert error.value.detail == "Insufficient stock"
    assert item.quantity == original_quantity


@pytest.mark.parametrize("operation", ["get", "update", "adjust", "delete"])
def test_item_operations_return_not_found_for_missing_ids(db_session, operation):
    missing_id = 999

    with pytest.raises(HTTPException) as error:
        if operation == "get":
            get_item(missing_id, db_session)
        elif operation == "update":
            update_item(missing_id, ItemUpdate(name="Updated item"), db_session)
        elif operation == "adjust":
            adjust_stock(missing_id, StockAdjust(delta=1), db_session)
        else:
            delete_item(missing_id, db_session)

    assert error.value.status_code == 404
    assert error.value.detail == "Item not found"
