from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers import demo_token, unique_value


def test_reject_a_duplicate_sku():
    """Reject a duplicate SKU"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = demo_token(api)
        if token is None:
            blocked = api.get("/api/items")
            assert blocked.status_code == 401, blocked.text
            return
        headers = {"Authorization": f"Bearer {token}"}
        sku = unique_value("DUPLICATE-SKU")
        original = api.post(
            "/api/items",
            json={
                "sku": sku,
                "name": unique_value("ORIGINAL-ITEM"),
                "description": unique_value("ORIGINAL-DESCRIPTION"),
                "quantity": 2,
                "location": "QA-D-01",
                "min_stock": 1,
            },
            headers=headers,
        )
        assert original.status_code == 201, original.text
        original_id = original.json()["id"]

        duplicate = api.post(
            "/api/items",
            json={
                "sku": sku,
                "name": unique_value("DUPLICATE-ITEM"),
                "description": unique_value("DUPLICATE-DESCRIPTION"),
                "quantity": 3,
                "location": "QA-D-02",
                "min_stock": 1,
            },
            headers=headers,
        )
        assert duplicate.status_code == 400, duplicate.text
        assert duplicate.json().get("detail") == "SKU already exists", "Duplicate SKU response did not explain the conflict"
        fetched = api.get(f"/api/items/{original_id}", headers=headers)
        assert fetched.status_code == 200, fetched.text
        assert fetched.json()["sku"] == sku, "Original item was not preserved after duplicate rejection"
