from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import auth_headers, sign_in


def test_sign_in_and_confirm_the_authenticated_user():
    """Sign in and confirm the authenticated user."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api, username="admin", password="admin123")
        response = api.get("/api/auth/me", headers=auth_headers(token))

    assert response.status_code == 200, response.text
    assert response.json().get("username") == "admin", "Authenticated user was not admin"
