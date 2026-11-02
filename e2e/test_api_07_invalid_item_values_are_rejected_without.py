from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import item_payload, sign_in, unique_value


def test_invalid_item_values_are_rejected_without_creating_an_item():
    """Invalid item values are rejected without creating an item."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        invalid_description = item_payload(
            "TOO-LONG-DESCRIPTION",
            sku=unique_value("INVALID-DESCRIPTION-SKU"),
            description="x" * 2001,
        )
        description_response = api.post("/api/items", json=invalid_description)
        assert description_response.status_code == 422, f"Oversized description was not rejected: {description_response.text}"

        invalid_quantity = item_payload(
            "TOO-LARGE-QUANTITY",
            sku=unique_value("INVALID-QUANTITY-SKU"),
            quantity=9_223_372_036_854_775_808,
        )
        quantity_response = api.post("/api/items", json=invalid_quantity)
        assert quantity_response.status_code == 422, f"Out-of-range quantity was not rejected: {quantity_response.text}"

        list_response = api.get("/api/items")
        assert list_response.status_code == 200, f"Listing inventory failed: {list_response.text}"
        skus = {item["sku"] for item in list_response.json()}
        assert invalid_description["sku"] not in skus, "Item with an oversized description was created"
        assert invalid_quantity["sku"] not in skus, "Item with an out-of-range quantity was created"
