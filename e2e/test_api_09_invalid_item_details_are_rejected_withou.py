from conftest import BASE, USER, PASSWORD

import time

import httpx

from api_helpers_3 import sign_in


def test_invalid_item_details_are_rejected_without_creating_a_record():
    """Invalid item details are rejected without creating a record."""
    unique = f"CYDIVO-QA-{time.time_ns()}"
    invalid_sku = f"{unique}-INVALID"
    item_sku = f"{unique}-DUPLICATE"
    item_name = f"{unique} duplicate-check item"

    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)

        invalid_response = api.post(
            "/api/items",
            json={
                "sku": invalid_sku,
                "name": "",
                "quantity": 2,
                "location": "A-01",
                "min_stock": 1,
            },
        )
        assert invalid_response.status_code == 422, invalid_response.text

        items_response = api.get("/api/items")
        assert items_response.status_code == 200, items_response.text
        assert not any(
            item["sku"] == invalid_sku for item in items_response.json()
        ), "The rejected blank-name item must not appear in inventory"

        item_body = {
            "sku": item_sku,
            "name": item_name,
            "quantity": 2,
            "location": "A-01",
            "min_stock": 1,
        }
        first_response = api.post("/api/items", json=item_body)
        assert first_response.status_code == 201, first_response.text
        created_item = first_response.json()

        duplicate_response = api.post("/api/items", json=item_body)
        assert duplicate_response.status_code == 400, duplicate_response.text

        retained_response = api.get(f"/api/items/{created_item['id']}")
        assert retained_response.status_code == 200, retained_response.text
        retained_item = retained_response.json()
        assert retained_item["sku"] == item_sku, "The first item should remain in inventory"
        assert retained_item["name"] == item_name, "The retained item should match the first creation"
