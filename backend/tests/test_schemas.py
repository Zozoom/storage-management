import pytest
from pydantic import ValidationError

from app.schemas import ItemCreate, ItemUpdate, StockAdjust


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sku", ""),
        ("sku", "S" * 65),
        ("name", ""),
        ("name", "N" * 129),
        ("quantity", -1),
        ("min_stock", -1),
    ],
)
def test_item_create_rejects_invalid_values(field, value):
    payload = {"sku": "SKU-1", "name": "Item", field: value}

    with pytest.raises(ValidationError):
        ItemCreate(**payload)


def test_item_update_accepts_omitted_fields():
    update = ItemUpdate()

    assert update.model_dump(exclude_unset=True) == {}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("name", "N" * 129),
        ("description", "D" * 2001),
        ("quantity", -1),
        ("location", "L" * 65),
        ("min_stock", -1),
    ],
)
def test_item_update_rejects_invalid_supplied_values(field, value):
    with pytest.raises(ValidationError):
        ItemUpdate(**{field: value})


@pytest.mark.parametrize("delta", [1, -1])
def test_stock_adjust_accepts_positive_and_negative_deltas(delta):
    adjustment = StockAdjust(delta=delta)

    assert adjustment.delta == delta
