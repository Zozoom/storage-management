from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import item_payload, sign_in


def test_create_an_item_and_retrieve_it_from_inventory():
    """Create an item and retrieve it from inventory"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        payload = item_payload("CREATE", quantity=6, min_stock=2)
        created = api.post("/api/items", json=payload, headers=headers)
        assert created.status_code == 201, created.text
        item = created.json()
        item_id = item["id"]

        fetched = api.get(f"/api/items/{item_id}", headers=headers)
        listing = api.get("/api/items", headers=headers)

    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["id"] == item_id, "Item retrieval returned a different item"
    for key in ("sku", "name", "description", "quantity", "location", "min_stock"):
        assert item.get(key) == payload[key], f"Created item has an unexpected {key}"
        assert fetched.json().get(key) == payload[key], f"Retrieved item has an unexpected {key}"
    assert listing.status_code == 200, listing.text
    assert any(entry.get("id") == item_id for entry in listing.json()), "Created item was not found in inventory"
