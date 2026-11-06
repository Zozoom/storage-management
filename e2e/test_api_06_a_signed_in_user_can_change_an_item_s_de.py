from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers_2 import sign_in, unique_item, unique_value


def test_signed_in_user_can_change_an_items_details():
    """A signed-in user can change an item's details."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        item = unique_item()
        created_response = api.post("/api/items", json=item)
        assert created_response.status_code == 201, f"Item creation failed: {created_response.text}"
        created = created_response.json()
        changed_name = unique_value("UPDATED-ITEM")
        changed_location = "QA-B-02"

        update_response = api.patch(
            f"/api/items/{created['id']}",
            json={"name": changed_name, "location": changed_location},
        )
        assert update_response.status_code == 200, f"Item update failed: {update_response.text}"
        updated = update_response.json()
        assert updated["name"] == changed_name, "Updated item name did not match"
        assert updated["location"] == changed_location, "Updated item location did not match"
        assert updated["sku"] == item["sku"], "Item SKU changed during the update"
        assert updated["quantity"] == item["quantity"], "Item quantity changed during the update"

        missing_response = api.patch("/api/items/2147483647", json={"location": "QA-C-03"})
        assert missing_response.status_code == 404, f"Missing-item update did not return 404: {missing_response.text}"
        assert missing_response.json().get("detail") == "Item not found", "Missing-item update did not identify the item as not found"

        retained_response = api.get(f"/api/items/{created['id']}")
        assert retained_response.status_code == 200, f"Updated item was not retained: {retained_response.text}"
        retained = retained_response.json()
        assert retained["name"] == changed_name, "Retained item name did not match the update"
        assert retained["location"] == changed_location, "Retained item location did not match the update"
