from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers_2 import sign_in, unique_value


def test_adjust_stock_and_verify_the_items_restocking_status():
    """Adjust stock and verify the item’s restocking status."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        tag = unique_value("stock")
        created = api.post(
            "/api/items",
            json={
                "sku": f"{tag}-SKU",
                "name": f"{tag}-Item",
                "quantity": 2,
                "location": f"{tag}-Location",
                "min_stock": 3,
            },
        )
        assert created.status_code == 201, f"Item creation failed: {created.text}"
        item_id = created.json()["id"]

        increased = api.post(f"/api/items/{item_id}/adjust", json={"delta": 1})
        assert increased.status_code == 200, f"Stock increase failed: {increased.text}"
        assert increased.json()["quantity"] == 3, "Stock increase returned the wrong quantity"

        decreased = api.post(f"/api/items/{item_id}/adjust", json={"delta": -1})
        assert decreased.status_code == 200, f"Stock decrease failed: {decreased.text}"
        assert decreased.json()["quantity"] == 2, "Stock decrease returned the wrong quantity"

        retrieved = api.get(f"/api/items/{item_id}")
        assert retrieved.status_code == 200, f"Item retrieval failed: {retrieved.text}"
        item = retrieved.json()
        assert item["quantity"] == 2, "Retrieved item does not have the final quantity of 2"
        assert item["low_stock"] is True, "Item with quantity below minimum stock was not marked low stock"