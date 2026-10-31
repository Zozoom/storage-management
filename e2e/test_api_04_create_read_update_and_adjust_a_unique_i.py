from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers import demo_token, unique_value


def test_create_read_update_and_adjust_a_unique_item():
    """Create, read, update, and adjust a unique item"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = demo_token(api)
        if token is None:
            blocked = api.get("/api/items")
            assert blocked.status_code == 401, blocked.text
            return
        headers = {"Authorization": f"Bearer {token}"}
        sku = unique_value("CRUD-SKU")
        original_name = unique_value("CRUD-ITEM")
        body = {
            "sku": sku,
            "name": original_name,
            "description": unique_value("DESCRIPTION"),
            "quantity": 2,
            "location": "QA-A-01",
            "min_stock": 3,
        }
        created = api.post("/api/items", json=body, headers=headers)
        assert created.status_code == 201, created.text
        item = created.json()
        item_id = item["id"]
        assert item["sku"] == sku, "Created item did not retain its unique SKU"
        assert item["name"] == original_name, "Created item did not retain its name"
        assert item["quantity"] == 2, "Created item did not retain its quantity"
        assert item["low_stock"] is True, "New item below its restock threshold was not marked low stock"

        fetched = api.get(f"/api/items/{item_id}", headers=headers)
        assert fetched.status_code == 200, fetched.text
        assert fetched.json()["id"] == item_id, "Item detail request returned the wrong item"
        assert fetched.json()["description"] == body["description"], "Item detail did not retain its description"

        changed_name = unique_value("UPDATED-ITEM")
        changed_location = "QA-B-02"
        patched = api.patch(
            f"/api/items/{item_id}",
            json={"name": changed_name, "location": changed_location},
            headers=headers,
        )
        assert patched.status_code == 200, patched.text
        updated = patched.json()
        assert updated["name"] == changed_name, "PATCH did not update the item name"
        assert updated["location"] == changed_location, "PATCH did not update the item location"
        assert updated["quantity"] == 2, "PATCH changed an unsupplied quantity field"
        assert updated["sku"] == sku, "PATCH changed the item's SKU"

        adjusted = api.post(
            f"/api/items/{item_id}/adjust",
            json={"delta": 2},
            headers=headers,
        )
        assert adjusted.status_code == 200, adjusted.text
        assert adjusted.json()["quantity"] == 4, "Stock adjustment did not produce quantity 4"
        assert adjusted.json()["low_stock"] is False, "Adjusted item was not marked in stock"
        listing = api.get("/api/items", headers=headers)
        assert listing.status_code == 200, listing.text
        assert any(entry["id"] == item_id for entry in listing.json()), "Created item was missing from inventory"
