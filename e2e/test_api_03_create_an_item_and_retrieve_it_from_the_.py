from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import auth_headers, sign_in, unique_item


def test_create_an_item_and_retrieve_it_from_the_inventory():
    """Create an item and retrieve it from the inventory."""
    item = unique_item(quantity=4, min_stock=5)
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = auth_headers(token)
        created = api.post("/api/items", json=item, headers=headers)
        assert created.status_code == 201, created.text
        created_data = created.json()

        individual = api.get(f"/api/items/{created_data['id']}", headers=headers)
        inventory = api.get("/api/items", headers=headers)

    assert created_data.get("sku") == item["sku"], "Created item SKU did not match"
    assert created_data.get("name") == item["name"], "Created item name did not match"
    assert created_data.get("description") == item["description"], "Created item description did not match"
    assert created_data.get("quantity") == item["quantity"], "Created item quantity did not match"
    assert created_data.get("location") == item["location"], "Created item location did not match"
    assert created_data.get("min_stock") == item["min_stock"], "Created item minimum stock did not match"
    assert created_data.get("low_stock") is True, "Created item should be marked low stock"
    assert individual.status_code == 200, individual.text
    assert individual.json().get("id") == created_data["id"], "Individual read returned a different item"
    assert any(row.get("id") == created_data["id"] for row in inventory.json()), "Inventory list omitted the created item"
