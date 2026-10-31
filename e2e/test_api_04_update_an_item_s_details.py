from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import auth_headers, sign_in, unique_item


def test_update_an_items_details():
    """Update an item's details."""
    item = unique_item()
    changes = {
        "name": f"{item['name']} updated",
        "description": f"{item['description']} updated",
        "quantity": 2,
        "location": f"{item['location']}-UPDATED",
        "min_stock": 7,
    }

    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = auth_headers(token)
        created = api.post("/api/items", json=item, headers=headers)
        assert created.status_code == 201, created.text
        item_id = created.json()["id"]

        updated = api.patch(f"/api/items/{item_id}", json=changes, headers=headers)
        assert updated.status_code == 200, updated.text
        retrieved = api.get(f"/api/items/{item_id}", headers=headers)

    assert retrieved.status_code == 200, retrieved.text
    data = retrieved.json()
    for field, expected in changes.items():
        assert data.get(field) == expected, f"Updated item field {field!r} did not match"
    assert data.get("low_stock") is True, "Updated item should be marked low stock"
