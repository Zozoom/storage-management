from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers_2 import sign_in, unique_item


def test_stock_cannot_be_adjusted_above_the_supported_maximum():
    """Stock cannot be adjusted above the supported maximum."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        maximum = 2147483647
        item = unique_item(quantity=maximum, min_stock=maximum)
        created_response = api.post("/api/items", json=item)
        assert created_response.status_code == 201, f"Item creation failed: {created_response.text}"
        created = created_response.json()
        assert created["quantity"] == maximum, "Created item did not retain the maximum quantity"

        adjustment_response = api.post(
            f"/api/items/{created['id']}/adjust",
            json={"delta": 1},
        )
        assert adjustment_response.status_code == 422, f"Over-maximum adjustment did not return 422: {adjustment_response.text}"
        assert "maximum" in adjustment_response.json().get("detail", "").lower(), "Over-maximum adjustment response did not explain the maximum quantity"

        retrieved_response = api.get(f"/api/items/{created['id']}")
        assert retrieved_response.status_code == 200, f"Maximum-quantity item could not be retrieved: {retrieved_response.text}"
        assert retrieved_response.json()["quantity"] == maximum, "Rejected adjustment changed the item's quantity"
