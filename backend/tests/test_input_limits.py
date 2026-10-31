import asyncio

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.main import MAX_REQUEST_BODY_BYTES, RequestBodyLimitMiddleware
from app.routers.items import _adjusted_quantity
from app.schemas import (
    MAX_DESCRIPTION_LENGTH,
    SQLITE_INTEGER_MAX,
    SQLITE_INTEGER_MIN,
    ItemCreate,
    ItemUpdate,
    StockAdjust,
)


def test_item_schemas_limit_description_length():
    for schema, payload in (
        (ItemCreate, {"sku": "SKU-1", "name": "Item"}),
        (ItemUpdate, {}),
    ):
        schema(description="d" * MAX_DESCRIPTION_LENGTH, **payload)
        with pytest.raises(ValidationError):
            schema(description="d" * (MAX_DESCRIPTION_LENGTH + 1), **payload)


def test_item_schemas_bound_integer_fields_to_sqlite_range():
    ItemCreate(sku="SKU-1", name="Item", quantity=SQLITE_INTEGER_MAX, min_stock=SQLITE_INTEGER_MAX)
    ItemUpdate(quantity=SQLITE_INTEGER_MAX, min_stock=SQLITE_INTEGER_MAX)
    for schema, payload in (
        (ItemCreate, {"sku": "SKU-1", "name": "Item", "quantity": SQLITE_INTEGER_MAX + 1}),
        (ItemCreate, {"sku": "SKU-1", "name": "Item", "min_stock": SQLITE_INTEGER_MAX + 1}),
        (ItemUpdate, {"quantity": SQLITE_INTEGER_MAX + 1}),
        (ItemUpdate, {"min_stock": SQLITE_INTEGER_MAX + 1}),
    ):
        with pytest.raises(ValidationError):
            schema(**payload)


def test_item_schemas_reject_empty_and_overlong_sku_and_name():
    for payload in (
        {"sku": "", "name": "Item"},
        {"sku": "s" * 65, "name": "Item"},
        {"sku": "SKU-1", "name": ""},
        {"sku": "SKU-1", "name": "n" * 129},
    ):
        with pytest.raises(ValidationError):
            ItemCreate(**payload)


def test_item_schemas_reject_negative_quantity_and_min_stock():
    for schema, payload in (
        (ItemCreate, {"sku": "SKU-1", "name": "Item", "quantity": -1}),
        (ItemCreate, {"sku": "SKU-1", "name": "Item", "min_stock": -1}),
        (ItemUpdate, {"quantity": -1}),
        (ItemUpdate, {"min_stock": -1}),
    ):
        with pytest.raises(ValidationError):
            schema(**payload)


def test_item_schemas_accept_partial_updates_and_nullable_descriptions():
    assert ItemUpdate(quantity=3).model_dump(exclude_unset=True) == {"quantity": 3}
    assert ItemUpdate(description=None).model_dump(exclude_unset=True) == {"description": None}
    assert ItemCreate(sku="SKU-1", name="Item", description=None).description is None


def test_item_create_uses_defaults_for_omitted_fields():
    item = ItemCreate(sku="SKU-1", name="Item")

    assert item.description is None
    assert item.quantity == 0
    assert item.location == "A-01"
    assert item.min_stock == 5


def test_stock_adjustment_schema_bounds_delta_to_sqlite_range():
    StockAdjust(delta=SQLITE_INTEGER_MIN)
    StockAdjust(delta=SQLITE_INTEGER_MAX)
    for delta in (SQLITE_INTEGER_MIN - 1, SQLITE_INTEGER_MAX + 1):
        with pytest.raises(ValidationError):
            StockAdjust(delta=delta)


def test_adjusted_quantity_rejects_result_above_sqlite_range():
    with pytest.raises(HTTPException) as exc_info:
        _adjusted_quantity(SQLITE_INTEGER_MAX, 1)

    assert exc_info.value.status_code == 422


def test_adjusted_quantity_preserves_insufficient_stock_error():
    with pytest.raises(HTTPException) as exc_info:
        _adjusted_quantity(0, -1)

    assert exc_info.value.status_code == 400


def test_request_body_limit_rejects_oversized_body():
    async def run_test():
        app_called = False
        messages = []
        chunks = [
            {"type": "http.request", "body": b"x" * (MAX_REQUEST_BODY_BYTES + 1), "more_body": False}
        ]

        async def receive():
            return chunks.pop(0)

        async def send(message):
            messages.append(message)

        async def downstream(scope, receive, send):
            nonlocal app_called
            app_called = True

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/api/items",
            "raw_path": b"/api/items",
            "query_string": b"",
            "root_path": "",
            "headers": [],
            "client": ("test", 1),
            "server": ("test", 80),
        }

        middleware = RequestBodyLimitMiddleware(downstream)
        await middleware(scope, receive, send)

        assert not app_called
        assert messages[0]["type"] == "http.response.start"
        assert messages[0]["status"] == 413

    asyncio.run(run_test())
