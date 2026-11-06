from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers_2 import sign_in, unique_item


def test_signed_in_user_can_adjust_stock_without_removing_more_than_available():
    """A signed-in user can adjust stock without removing more than is available."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        item = unique_item(quantity=2, min_stock=2)
        created_response = api.post("/api/items", json=item)
        assert created_response.status_code == 201, f"Item creation failed: {created_response.text}"
        created = created_response.json()

        adjustment_response = api.post(
            f"/api/items/{created['id']}/adjust",
            json={"delta": -1},
        )
        assert adjustment_response.status_code == 200, f"Stock adjustment failed: {adjustment_response.text}"
        adjusted = adjustment_response.json()
        assert adjusted["quantity"] == 1, "Adjusted quantity was not 1"
        assert adjusted["low_stock"] is True, "Adjusted item was not marked as low stock"

        retrieved_response = api.get(f"/api/items/{created['id']}")
        assert retrieved_response.status_code == 200, f"Adjusted item could not be retrieved: {retrieved_response.text}"
        retrieved = retrieved_response.json()
        assert retrieved["quantity"] == 1, "Retrieved item quantity did not reflect the adjustment"
        assert retrieved["low_stock"] is True, "Retrieved item was not marked as low stock"
