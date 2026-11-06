from conftest import BASE, USER, PASSWORD

import time

import httpx

from api_helpers import sign_in


def test_create_and_retrieve_inventory_item():
    """Create an item and retrieve it from inventory."""
    unique = f"CYDIVO-QA-{int(time.time() * 1000)}"
    item_data = {
        "sku": f"{unique}-SKU",
        "name": f"{unique}-item",
        "description": f"{unique}-description",
        "quantity": 7,
        "location": f"{unique}-bin",
        "min_stock": 10,
    }

    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        created = api.post("/api/items", json=item_data, headers=headers)
        assert created.status_code == 201, created.text
        created_item = created.json()
        item_id = created_item.get("id")
        assert item_id is not None, "Created item response did not contain an item ID"
        assert created_item.get("sku") == item_data["sku"], "Created item SKU differs from the submitted value"
        assert created_item.get("name") == item_data["name"], "Created item name differs from the submitted value"
        assert created_item.get("description") == item_data["description"], "Created item description differs from the submitted value"
        assert created_item.get("quantity") == item_data["quantity"], "Created item quantity differs from the submitted value"
        assert created_item.get("location") == item_data["location"], "Created item location differs from the submitted value"
        assert created_item.get("min_stock") == item_data["min_stock"], "Created item minimum stock differs from the submitted value"
        assert created_item.get("low_stock") is True, "Created item should be flagged as low stock"

        retrieved = api.get(f"/api/items/{item_id}", headers=headers)
        assert retrieved.status_code == 200, retrieved.text
        assert retrieved.json().get("sku") == item_data["sku"], "Item-by-ID response did not contain the created item"
        assert retrieved.json().get("low_stock") is True, "Item-by-ID response has an incorrect low-stock status"

        inventory = api.get("/api/items", headers=headers)
        assert inventory.status_code == 200, inventory.text
        listed_item = next((item for item in inventory.json() if item.get("id") == item_id), None)
        assert listed_item is not None, "Inventory list did not contain the created item"
        assert listed_item.get("sku") == item_data["sku"], "Inventory list returned an unexpected SKU for the created item"
        assert listed_item.get("low_stock") is True, "Inventory list has an incorrect low-stock status for the created item"
