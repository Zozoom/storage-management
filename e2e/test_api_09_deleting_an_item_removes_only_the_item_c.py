from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import create_item, item_payload, sign_in


def test_deleting_an_item_removes_only_the_item_created_for_this_test():
    """Deleting an item removes only the item created for this test."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        created = create_item(api, item_payload("DELETE-OWN-ITEM"))

        deleted = api.delete(f"/api/items/{created['id']}")
        assert deleted.status_code == 204, f"Deleting the test-created item failed: {deleted.text}"
        item_response = api.get(f"/api/items/{created['id']}")
        assert item_response.status_code == 404, f"Deleted item was not absent: {item_response.text}"
        list_response = api.get("/api/items")
        assert list_response.status_code == 200, f"Listing inventory after deletion failed: {list_response.text}"
        assert all(item["id"] != created["id"] for item in list_response.json()), "Deleted item remains in the inventory list"
