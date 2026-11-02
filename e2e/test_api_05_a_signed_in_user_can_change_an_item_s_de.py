from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import create_item, item_payload, sign_in, unique_value


def test_a_signed_in_user_can_change_an_items_details():
    """A signed-in user can change an item's details."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        payload = item_payload("UPDATE-DETAILS")
        created = create_item(api, payload)
        updates = {
            "name": unique_value("UPDATED-NAME"),
            "description": unique_value("UPDATED-DESCRIPTION"),
            "location": unique_value("UPDATED-LOCATION"),
            "min_stock": 9,
        }

        response = api.patch(f"/api/items/{created['id']}", json=updates)
        assert response.status_code == 200, f"Updating item details failed: {response.text}"
        updated = response.json()
        for field, value in updates.items():
            assert updated[field] == value, f"Updated item has the wrong {field}"
        assert updated["sku"] == payload["sku"], "Update unexpectedly changed the item's SKU"
        assert updated["quantity"] == payload["quantity"], "Update unexpectedly changed the item's quantity"
