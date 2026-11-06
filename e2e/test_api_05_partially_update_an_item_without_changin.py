from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import item_payload, sign_in


def test_partially_update_an_item_without_changing_its_other_fields():
    """Partially update an item without changing its other fields"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        payload = item_payload("PATCH", quantity=7, min_stock=3)
        created = api.post("/api/items", json=payload, headers=headers)
        assert created.status_code == 201, created.text
        item_id = created.json()["id"]
        updated_name = f"{payload['name']} updated"

        response = api.patch(
            f"/api/items/{item_id}",
            json={"name": updated_name},
            headers=headers,
        )

    assert response.status_code == 200, response.text
    updated = response.json()
    assert updated.get("name") == updated_name, "Item name was not updated"
    for key in ("sku", "location", "quantity", "min_stock"):
        assert updated.get(key) == payload[key], f"Partial update changed the item's {key}"
