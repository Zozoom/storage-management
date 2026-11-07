from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import sign_in, unique_value


def test_create_item_and_retrieve_it_from_inventory():
    """Create an item and retrieve it from the inventory."""
    sku = unique_value("SKU")
    name = unique_value("ITEM")
    item_data = {
        "sku": sku,
        "name": name,
        "description": unique_value("DESCRIPTION"),
        "quantity": 17,
        "location": "CYDIVO-QA-A-01",
        "min_stock": 4,
    }

    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        create_response = api.post("/api/items", json=item_data, headers=headers)
        assert create_response.status_code == 201, f"Item creation failed: {create_response.text}"
        created = create_response.json()
        assert all(created.get(field) == value for field, value in item_data.items()), f"Created item did not contain the submitted values: {create_response.text}"

        item_id = created.get("id")
        assert item_id is not None, f"Item creation response did not include an ID: {create_response.text}"

        item_response = api.get(f"/api/items/{item_id}", headers=headers)
        assert item_response.status_code == 200, f"Could not retrieve the created item: {item_response.text}"
        assert item_response.json().get("id") == item_id, f"Individual item response had the wrong ID: {item_response.text}"
        assert all(item_response.json().get(field) == value for field, value in item_data.items()), f"Individual item response did not match the submitted values: {item_response.text}"

        list_response = api.get("/api/items", headers=headers)
        assert list_response.status_code == 200, f"Could not retrieve the inventory list: {list_response.text}"
        listed_item = next((item for item in list_response.json() if item.get("id") == item_id), None)
        assert listed_item is not None, f"Created item was missing from the inventory list: {list_response.text}"
        assert all(listed_item.get(field) == value for field, value in item_data.items()), f"Inventory list item did not match the submitted values: {listed_item}"
