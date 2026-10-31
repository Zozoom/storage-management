from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers import demo_token, unique_value


def test_delete_only_a_separately_created_test_item():
    """Delete only a separately created test item"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = demo_token(api)
        if token is None:
            blocked = api.get("/api/items")
            assert blocked.status_code == 401, blocked.text
            return
        headers = {"Authorization": f"Bearer {token}"}
        sku = unique_value("DELETE-SKU")
        created = api.post(
            "/api/items",
            json={
                "sku": sku,
                "name": unique_value("DELETE-ITEM"),
                "description": unique_value("DELETE-DESCRIPTION"),
                "quantity": 2,
                "location": "QA-E-01",
                "min_stock": 1,
            },
            headers=headers,
        )
        assert created.status_code == 201, created.text
        item_id = created.json()["id"]

        deleted = api.delete(f"/api/items/{item_id}", headers=headers)
        assert deleted.status_code == 204, deleted.text
        fetched = api.get(f"/api/items/{item_id}", headers=headers)
        assert fetched.status_code == 404, fetched.text
