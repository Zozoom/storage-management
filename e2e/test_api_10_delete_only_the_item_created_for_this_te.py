from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers_3 import sign_in, unique_value


def test_delete_only_the_item_created_for_this_test():
    """Delete only the item created for this test."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        value = unique_value()
        created = api.post(
            "/api/items",
            json={
                "sku": f"{value}-SKU",
                "name": f"{value} item",
                "description": "Created by the API test.",
                "quantity": 1,
                "location": "A-01",
                "min_stock": 1,
            },
        )
        assert created.status_code == 201, created.text
        item_id = created.json()["id"]

        deleted = api.delete(f"/api/items/{item_id}")
        assert deleted.status_code == 204, deleted.text

        lookup = api.get(f"/api/items/{item_id}")
        assert lookup.status_code == 404, lookup.text
