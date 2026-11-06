import pytest
from pydantic import ValidationError

from app.schemas import ItemCreate


@pytest.mark.parametrize(
    ("field", "minimum", "maximum"),
    (("sku", 1, 64), ("name", 1, 128)),
)
def test_item_create_accepts_minimum_and_maximum_string_lengths(field, minimum, maximum):
    for length in (minimum, maximum):
        item = ItemCreate(sku="S", name="N", **{field: "x" * length})
        assert len(getattr(item, field)) == length


@pytest.mark.parametrize(
    ("field", "value"),
    (("sku", ""), ("sku", "x" * 65), ("name", ""), ("name", "x" * 129)),
)
def test_item_create_rejects_invalid_sku_and_name_lengths(field, value):
    with pytest.raises(ValidationError):
        ItemCreate(sku="S", name="N", **{field: value})


@pytest.mark.parametrize("field", ("quantity", "min_stock"))
def test_item_create_rejects_negative_stock_values(field):
    with pytest.raises(ValidationError):
        ItemCreate(sku="SKU-1", name="Item", **{field: -1})


def test_item_create_accepts_valid_defaults_and_optional_fields():
    item = ItemCreate(sku="SKU-1", name="Item", description=None)

    assert item.description is None
    assert item.quantity == 0
    assert item.location == "A-01"
    assert item.min_stock == 5
