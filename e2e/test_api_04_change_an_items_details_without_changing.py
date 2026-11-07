from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers_2 import sign_in, unique_value


def test_change_an_items_details_without_changing_its_sku():
    """Change an item’s details without changing its SKU."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        tag = unique_value("details")
        original_sku = f"{tag}-SKU"
        created = api.post(
            "/api/items",
            json={
                "sku": original_sku,
                "name": f"{tag}-Original",
                "description": "Original description",
                "quantity": 1,
                "location": "A-01",
                "min_stock": 0,
            },
        )
        assert created.status_code == 201, f"Item creation failed: {created.text}"
        item_id = created.json()["id"]

        updated_name = f"{tag}-Updated"
        updated_description = f"{tag} updated description"
        updated_location = f"{tag}-Location"
        changed = api.patch(
            f"/api/items/{item_id}",
            json={
                "name": updated_name,
                "description": updated_description,
                "location": updated_location,
            },
        )
        assert changed.status_code == 200, f"Item update failed: {changed.text}"
        changed_item = changed.json()
        assert changed_item["name"] == updated_name, "Update response has the wrong name"
        assert changed_item["description"] == updated_description, "Update response has the wrong description"
        assert changed_item["location"] == updated_location, "Update response has the wrong location"
        assert changed_item["sku"] == original_sku, "Update response changed the original SKU"

        retrieved = api.get(f"/api/items/{item_id}")
        assert retrieved.status_code == 200, f"Item retrieval failed: {retrieved.text}"
        item = retrieved.json()
        assert item["name"] == updated_name, "Retrieved item has the wrong updated name"
        assert item["description"] == updated_description, "Retrieved item has the wrong updated description"
        assert item["location"] == updated_location, "Retrieved item has the wrong updated location"
        assert item["sku"] == original_sku, "Retrieved item did not retain its original SKU"