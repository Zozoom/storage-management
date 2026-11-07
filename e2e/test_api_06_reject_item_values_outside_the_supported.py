from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers_2 import sign_in, unique_value


def test_reject_item_values_outside_the_supported_limits():
    """Reject item values outside the supported limits."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        tag = unique_value("limits")
        overlong = api.post(
            "/api/items",
            json={
                "sku": f"{tag}-LONG-SKU",
                "name": f"{tag}-Overlong-description",
                "description": "x" * 2001,
                "quantity": 0,
                "location": "A-01",
                "min_stock": 0,
            },
        )
        assert overlong.status_code == 422, f"Overlong description was not rejected: {overlong.text}"

        maximum = 2_147_483_647
        created = api.post(
            "/api/items",
            json={
                "sku": f"{tag}-MAX-SKU",
                "name": f"{tag}-Maximum-stock-item",
                "quantity": maximum,
                "location": f"{tag}-Location",
                "min_stock": 0,
            },
        )
        assert created.status_code == 201, f"Maximum-quantity item creation failed: {created.text}"
        item_id = created.json()["id"]

        adjusted = api.post(f"/api/items/{item_id}/adjust", json={"delta": 1})
        assert adjusted.status_code == 400, f"Adjustment beyond maximum was not rejected: {adjusted.text}"

        retrieved = api.get(f"/api/items/{item_id}")
        assert retrieved.status_code == 200, f"Item retrieval failed: {retrieved.text}"
        assert retrieved.json()["quantity"] == maximum, "Rejected adjustment changed the item quantity"