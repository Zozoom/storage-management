from conftest import BASE, USER, PASSWORD

import httpx


def test_require_authentication_to_list_inventory():
    """Require authentication to list inventory"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        response = api.get("/api/items")

    assert response.status_code == 401, response.text
    assert response.json().get("detail"), "Unauthenticated response did not explain the authorization failure"
