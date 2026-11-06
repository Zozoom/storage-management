from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers_2 import sign_in, unique_value


def test_reject_request_body_larger_than_limit():
    """Reject a request body larger than the allowed limit."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        unique = unique_value()
        sku = f"{unique}-SKU"
        response = api.post(
            "/api/items",
            headers=headers,
            json={
                "sku": sku,
                "name": f"{unique}-Item",
                "quantity": 1,
                "location": f"{unique}-Location",
                "description": "x" * (17 * 1024),
            },
        )
        assert response.status_code == 413, f"Oversized request was not rejected: {response.text}"

        listing = api.get("/api/items", headers=headers)
        assert listing.status_code == 200, f"Could not verify item listing: {listing.text}"
        assert all(item["sku"] != sku for item in listing.json()), "Oversized request created an item"
