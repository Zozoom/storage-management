from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import create_item, item_payload, sign_in, unique_value


def test_a_signed_in_user_can_create_and_retrieve_a_uniquely_identified_item():
    """A signed-in user can create and retrieve a uniquely identified item."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        payload = item_payload("CREATE-RETRIEVE", name=unique_value("CREATE-RETRIEVE-NAME"))
        created = create_item(api, payload)

        assert created["sku"] == payload["sku"], "Created item has the wrong SKU"
        assert created["name"] == payload["name"], "Created item has the wrong name"
        assert created["description"] == payload["description"], "Created item has the wrong description"
        assert created["quantity"] == payload["quantity"], "Created item has the wrong quantity"
        assert created["location"] == payload["location"], "Created item has the wrong location"
        assert created["min_stock"] == payload["min_stock"], "Created item has the wrong minimum stock"
        assert created["low_stock"] is False, "Created item's low-stock status is incorrect"

        item_response = api.get(f"/api/items/{created['id']}")
        assert item_response.status_code == 200, f"Retrieving the created item failed: {item_response.text}"
        assert item_response.json() == created, "Item endpoint returned different item data"
        list_response = api.get("/api/items")
        assert list_response.status_code == 200, f"Listing inventory failed: {list_response.text}"
        listed = [item for item in list_response.json() if item["id"] == created["id"]]
        assert listed == [created], "Inventory list did not contain the created item"
