from conftest import BASE, USER, PASSWORD

import httpx
import time

from api_helpers_3 import sign_in


def test_delete_an_item_created_for_this_test():
    """Delete an item created for this test."""
    unique = f"CYDIVO-QA-{int(time.time() * 1000)}"
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        created = api.post(
            "/api/items",
            headers=headers,
            json={
                "sku": unique,
                "name": unique,
                "description": "Created by an API test.",
                "quantity": 1,
                "location": "QA-01",
                "min_stock": 0,
            },
        )
        assert created.status_code == 201, f"Item creation failed: {created.text}"
        item_id = created.json()["id"]

        deleted = api.delete(f"/api/items/{item_id}", headers=headers)
        assert deleted.status_code == 204, f"Item deletion failed: {deleted.text}"

        retrieved = api.get(f"/api/items/{item_id}", headers=headers)
        assert retrieved.status_code == 404, f"Deleted item was not absent: {retrieved.text}"
