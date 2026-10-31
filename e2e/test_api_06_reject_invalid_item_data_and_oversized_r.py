from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import auth_headers, sign_in, unique_item


def test_reject_invalid_item_data_and_oversized_requests():
    """Reject invalid item data and oversized requests."""
    item = unique_item()
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = auth_headers(token)
        created = api.post("/api/items", json=item, headers=headers)
        assert created.status_code == 201, created.text
        item_id = created.json()["id"]

        duplicate = api.post("/api/items", json=item, headers=headers)
        long_description = api.post(
            "/api/items",
            json=unique_item(description="D" * 2001),
            headers=headers,
        )
        out_of_range_quantity = api.post(
            "/api/items",
            json=unique_item(quantity=9223372036854775808),
            headers=headers,
        )
        oversized_body = api.post(
            "/api/items",
            json=unique_item(description="O" * (1024 * 1024 + 100)),
            headers=headers,
        )
        original = api.get(f"/api/items/{item_id}", headers=headers)

    assert duplicate.status_code in (400, 422), duplicate.text
    assert long_description.status_code in (400, 422), long_description.text
    assert out_of_range_quantity.status_code in (400, 422), out_of_range_quantity.text
    assert oversized_body.status_code == 413, oversized_body.text
    assert original.status_code == 200, original.text
    assert original.json().get("sku") == item["sku"], "Original item was not retrievable after rejected requests"
