from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import auth_headers, sign_in, unique_item


def test_adjust_stock_and_handle_insufficient_stock():
    """Adjust stock and handle insufficient stock."""
    item = unique_item(quantity=1, min_stock=3)
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = auth_headers(token)
        created = api.post("/api/items", json=item, headers=headers)
        assert created.status_code == 201, created.text
        item_id = created.json()["id"]

        increase = api.post(f"/api/items/{item_id}/adjust", json={"delta": 1}, headers=headers)
        decrease = api.post(f"/api/items/{item_id}/adjust", json={"delta": -1}, headers=headers)
        excessive_decrease = api.post(
            f"/api/items/{item_id}/adjust", json={"delta": -2}, headers=headers
        )
        retrieved = api.get(f"/api/items/{item_id}", headers=headers)

    assert increase.status_code == 200, increase.text
    assert increase.json().get("quantity") == 2, "Increasing stock did not produce quantity 2"
    assert decrease.status_code == 200, decrease.text
    assert decrease.json().get("quantity") == 1, "Decreasing stock did not produce quantity 1"
    assert excessive_decrease.status_code == 400, excessive_decrease.text
    assert retrieved.status_code == 200, retrieved.text
    assert retrieved.json().get("quantity") == 1, "Rejected adjustment changed the item quantity"
    assert retrieved.json().get("low_stock") is True, "Item at quantity 1 should be marked low stock"
