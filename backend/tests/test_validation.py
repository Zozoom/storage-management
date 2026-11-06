import asyncio

import pytest
from pydantic import ValidationError

from app.main import MAX_REQUEST_BODY_BYTES, RequestBodyLimitMiddleware
from app.schemas import ItemCreate, ItemUpdate, StockAdjust


def test_item_create_accepts_sku_and_name_length_boundaries():
    ItemCreate(sku="S", name="N")
    ItemCreate(sku="S" * 64, name="N" * 128)


def test_item_create_rejects_empty_or_oversized_sku_and_name():
    for values in (
        {"sku": "", "name": "Item"},
        {"sku": "S" * 65, "name": "Item"},
        {"sku": "SKU-1", "name": ""},
        {"sku": "SKU-1", "name": "N" * 129},
    ):
        with pytest.raises(ValidationError):
            ItemCreate(**values)


def test_item_create_requires_sku_and_name():
    with pytest.raises(ValidationError):
        ItemCreate(name="Item")
    with pytest.raises(ValidationError):
        ItemCreate(sku="SKU-1")


def test_item_create_accepts_nonnegative_quantity_and_min_stock_boundaries():
    ItemCreate(sku="SKU-1", name="Item", quantity=0, min_stock=0)
    ItemCreate(
        sku="SKU-2",
        name="Item",
        quantity=1_000_000_000,
        min_stock=1_000_000_000,
    )


def test_item_create_rejects_negative_quantity_and_min_stock():
    with pytest.raises(ValidationError):
        ItemCreate(sku="SKU-1", name="Item", quantity=-1)
    with pytest.raises(ValidationError):
        ItemCreate(sku="SKU-1", name="Item", min_stock=-1)


def test_item_update_supports_omitted_and_null_fields():
    assert ItemUpdate().model_dump(exclude_unset=True) == {}

    update = ItemUpdate(
        name=None,
        description=None,
        quantity=None,
        location=None,
        min_stock=None,
    )
    assert update.model_dump(exclude_unset=True) == {
        "name": None,
        "description": None,
        "quantity": None,
        "location": None,
        "min_stock": None,
    }


def test_item_update_rejects_invalid_non_null_values():
    with pytest.raises(ValidationError):
        ItemUpdate(name="")
    with pytest.raises(ValidationError):
        ItemUpdate(quantity=-1)
    with pytest.raises(ValidationError):
        ItemUpdate(min_stock=-1)


def test_stock_adjustment_accepts_range_boundaries_and_rejects_invalid_input():
    StockAdjust(delta=-1_000_000_000)
    StockAdjust(delta=1_000_000_000)

    with pytest.raises(ValidationError):
        StockAdjust(delta=1_000_000_001)
    with pytest.raises(ValidationError):
        StockAdjust(delta=-1_000_000_001)
    with pytest.raises(ValidationError):
        StockAdjust()
    with pytest.raises(ValidationError):
        StockAdjust(delta="not-a-number")


def test_item_schemas_reject_oversized_descriptions_and_quantities():
    with pytest.raises(ValidationError):
        ItemCreate(sku="SKU-1", name="Item", description="x" * 2001)
    with pytest.raises(ValidationError):
        ItemUpdate(description="x" * 2001)
    with pytest.raises(ValidationError):
        ItemCreate(sku="SKU-1", name="Item", quantity=1_000_000_001)
    with pytest.raises(ValidationError):
        ItemUpdate(quantity=1_000_000_001)


def test_stock_adjustment_rejects_out_of_range_delta():
    with pytest.raises(ValidationError):
        StockAdjust(delta=1_000_000_001)
    with pytest.raises(ValidationError):
        StockAdjust(delta=-1_000_000_001)


def test_request_body_limit_returns_controlled_413_response():
    async def run_test():
        app_called = False

        async def downstream(scope, receive, send):
            nonlocal app_called
            app_called = True

        middleware = RequestBodyLimitMiddleware(downstream)
        messages = [
            {
                "type": "http.request",
                "body": b"x" * (MAX_REQUEST_BODY_BYTES + 1),
                "more_body": False,
            }
        ]

        async def receive():
            return messages.pop(0)

        sent = []

        async def send(message):
            sent.append(message)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/api/items",
            "raw_path": b"/api/items",
            "query_string": b"",
            "headers": [],
            "server": ("testserver", 80),
            "client": ("testclient", 1234),
            "root_path": "",
        }

        await middleware(scope, receive, send)

        assert not app_called
        assert sent[0]["status"] == 413
        assert sent[1]["body"] == b'{"detail":"Request body too large"}'

    asyncio.run(run_test())
