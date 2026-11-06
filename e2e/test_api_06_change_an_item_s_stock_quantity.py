from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import item_payload, sign_in


def test_change_an_items_stock_quantity():
    """Change an item's stock quantity"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        payload = item_payload("ADJUST", quantity=5, min_stock=2)
        created = api.post("/api/items", json=payload, headers=headers)
        assert created.status_code == 201, created.text
        item_id = created.json()["id"]

        adjusted = api.post(
            f"/api/items/{item_id}/adjust",
            json={"delta": 3},
            headers=headers,
        )
        listing = api.get("/api/items", headers=headers)

    assert adjusted.status_code == 200, adjusted.text
    assert adjusted.json().get("quantity") == 8, "Stock adjustment did not set the quantity to 8"
    assert listing.status_code == 200, listing.text
    assert any(entry.get("id") == item_id for entry in listing.json()), "Adjusted item was not found in inventory"
