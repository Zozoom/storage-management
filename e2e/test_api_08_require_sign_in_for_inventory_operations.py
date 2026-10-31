from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import unique_item


def test_require_sign_in_for_inventory_operations():
    """Require sign-in for inventory operations."""
    item = unique_item()
    with httpx.Client(base_url=BASE, timeout=20) as api:
        listing = api.get("/api/items")
        creation = api.post("/api/items", json=item)
        individual = api.get("/api/items/1")

    assert listing.status_code == 401, listing.text
    assert creation.status_code == 401, creation.text
    assert individual.status_code == 401, individual.text
