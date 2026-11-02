import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models import Item, User
from app.routers.items import adjust_stock
from app.schemas import (
    MAX_DESCRIPTION_LENGTH,
    MAX_QUANTITY,
    ItemCreate,
    ItemUpdate,
    StockAdjust,
)


def test_item_descriptions_are_bounded():
    description = "x" * (MAX_DESCRIPTION_LENGTH + 1)

    with pytest.raises(ValidationError):
        ItemCreate(sku="SKU-1", name="Item", description=description)
    with pytest.raises(ValidationError):
        ItemUpdate(description=description)


def test_item_quantities_are_bounded():
    with pytest.raises(ValidationError):
        ItemCreate(sku="SKU-1", name="Item", quantity=MAX_QUANTITY + 1)
    with pytest.raises(ValidationError):
        ItemUpdate(quantity=MAX_QUANTITY + 1)


def test_stock_adjustment_delta_is_bounded():
    with pytest.raises(ValidationError):
        StockAdjust(delta=MAX_QUANTITY + 1)
    with pytest.raises(ValidationError):
        StockAdjust(delta=-MAX_QUANTITY - 1)


def test_stock_adjustment_rejects_result_above_maximum_without_writing(db_session):
    item = db_session.query(Item).first()
    item.quantity = MAX_QUANTITY
    db_session.commit()
    user = db_session.query(User).first()

    with pytest.raises(HTTPException) as exc_info:
        adjust_stock(item.id, StockAdjust(delta=1), db_session, user)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Quantity exceeds maximum allowed value"
    assert item.quantity == MAX_QUANTITY


@pytest.mark.parametrize(
    "values",
    [
        {"sku": "", "name": "Item"},
        {"sku": "x" * 65, "name": "Item"},
        {"sku": "SKU-1", "name": ""},
        {"sku": "SKU-1", "name": "x" * 129},
        {"sku": "SKU-1", "name": "Item", "quantity": -1},
        {"sku": "SKU-1", "name": "Item", "min_stock": -1},
    ],
    ids=["empty-sku", "oversized-sku", "empty-name", "oversized-name", "negative-quantity", "negative-min-stock"],
)
def test_item_create_rejects_invalid_boundary_values(values):
    with pytest.raises(ValidationError):
        ItemCreate(**values)


def test_item_update_accepts_omitted_optional_fields():
    update = ItemUpdate()

    assert update.model_dump(exclude_unset=True) == {}


@pytest.mark.parametrize(
    "values",
    [
        {"name": ""},
        {"name": "x" * 129},
        {"quantity": -1},
        {"min_stock": -1},
    ],
    ids=["empty-name", "oversized-name", "negative-quantity", "negative-min-stock"],
)
def test_item_update_rejects_invalid_provided_values(values):
    with pytest.raises(ValidationError):
        ItemUpdate(**values)


@pytest.mark.parametrize("delta", [5, 0, -5], ids=["positive", "zero", "negative"])
def test_stock_adjustment_accepts_positive_zero_and_negative_deltas(delta):
    assert StockAdjust(delta=delta).delta == delta
