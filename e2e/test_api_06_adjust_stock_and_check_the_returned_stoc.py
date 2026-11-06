from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers_2 import sign_in, unique_value


def test_stock_adjustment_returns_updated_stock_status():
    """Adjust stock and check the returned stock status."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        unique = unique_value()
        created = api.post(
            "/api/items",
            headers=headers,
            json={
                "sku": f"{unique}-SKU",
                "name": f"{unique}-Item",
                "quantity": 1,
                "location": f"{unique}-Location",
                "min_stock": 2,
            },
        )
        assert created.status_code == 201, f"Item creation failed: {created.text}"

        response = api.post(
            f"/api/items/{created.json()['id']}/adjust",
            headers=headers,
            json={"delta": 1},
        )
        assert response.status_code == 200, f"Stock adjustment failed: {response.text}"
        item = response.json()
        assert item["quantity"] == 2, "Adjusted quantity was not returned"
        assert item["low_stock"] is False, "Item is incorrectly marked as low stock"
