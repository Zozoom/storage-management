from conftest import BASE, USER, PASSWORD

import httpx


def test_inventory_requires_authentication():
    """Require authentication to access inventory."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        response = api.get("/api/items")

    assert response.status_code == 401, response.text
    assert not isinstance(response.json(), list), "Unauthenticated response returned inventory data"
