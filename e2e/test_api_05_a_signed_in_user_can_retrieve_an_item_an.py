from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers_2 import sign_in, unique_item


def test_signed_in_user_can_retrieve_an_item_and_missing_item_returns_not_found():
    """A signed-in user can retrieve an item and receives not found for a missing item."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        item = unique_item()
        created_response = api.post("/api/items", json=item)
        assert created_response.status_code == 201, f"Item creation failed: {created_response.text}"
        created = created_response.json()

        response = api.get(f"/api/items/{created['id']}")
        assert response.status_code == 200, f"Retrieving the created item failed: {response.text}"
        retrieved = response.json()
        assert retrieved["id"] == created["id"], "Retrieved item ID did not match the created item"
        assert retrieved["sku"] == item["sku"], "Retrieved item SKU did not match"
        assert retrieved["name"] == item["name"], "Retrieved item name did not match"
        assert retrieved["quantity"] == item["quantity"], "Retrieved item quantity did not match"
        assert retrieved["location"] == item["location"], "Retrieved item location did not match"

        missing_response = api.get("/api/items/2147483647")
        assert missing_response.status_code == 404, f"Missing-item request did not return 404: {missing_response.text}"
        assert missing_response.json().get("detail") == "Item not found", "Missing-item response did not identify the item as not found"

        retained_response = api.get(f"/api/items/{created['id']}")
        assert retained_response.status_code == 200, f"Created item was not retained: {retained_response.text}"
        assert retained_response.json()["sku"] == item["sku"], "Retained item SKU did not match the created item"
