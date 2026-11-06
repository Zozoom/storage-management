from conftest import BASE, USER, PASSWORD

import httpx


def test_inventory_cannot_be_listed_without_signing_in():
    """Inventory cannot be listed without signing in."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        response = api.get("/api/items")

    assert response.status_code == 401, response.text
    assert not isinstance(response.json(), list), "Unauthenticated inventory requests must not disclose inventory data"
