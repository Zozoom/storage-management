from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers import demo_token, unique_value


def test_reject_invalid_item_values_without_losing_valid_proof():
    """Reject invalid item values without losing valid proof"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = demo_token(api)
        if token is None:
            blocked = api.get("/api/items")
            assert blocked.status_code == 401, blocked.text
            return
        headers = {"Authorization": f"Bearer {token}"}
        valid_sku = unique_value("VALID-SKU")
        valid = api.post(
            "/api/items",
            json={
                "sku": valid_sku,
                "name": unique_value("VALID-ITEM"),
                "description": unique_value("VALID-DESCRIPTION"),
                "quantity": 2,
                "location": "QA-C-03",
                "min_stock": 1,
            },
            headers=headers,
        )
        assert valid.status_code == 201, valid.text
        valid_id = valid.json()["id"]

        invalid = api.post(
            "/api/items",
            json={
                "sku": unique_value("NEGATIVE-SKU"),
                "name": unique_value("NEGATIVE-ITEM"),
                "description": unique_value("NEGATIVE-DESCRIPTION"),
                "quantity": -1,
                "location": "QA-C-04",
                "min_stock": 1,
            },
            headers=headers,
        )
        assert invalid.status_code == 422, invalid.text
        fetched = api.get(f"/api/items/{valid_id}", headers=headers)
        assert fetched.status_code == 200, fetched.text
        assert fetched.json()["sku"] == valid_sku, "Valid proof item was not preserved"
