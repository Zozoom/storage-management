from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import item_payload, sign_in, unique_value


def test_reject_an_item_with_a_field_beyond_its_allowed_length():
    """Reject an item with a field beyond its allowed length"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        payload = item_payload("TOO-LONG")
        payload["sku"] = unique_value("TOO-LONG-SKU")
        payload["name"] = "N" * 129
        response = api.post("/api/items", json=payload, headers=headers)
        listing = api.get("/api/items", headers=headers)

    assert response.status_code == 422, response.text
    assert listing.status_code == 200, listing.text
    assert not any(entry.get("sku") == payload["sku"] for entry in listing.json()), "Invalid item was created"
