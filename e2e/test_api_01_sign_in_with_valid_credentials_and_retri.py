from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import sign_in


def test_sign_in_with_valid_credentials_and_retrieve_the_current_user():
    """Sign in with valid credentials and retrieve the current user"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        response = api.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200, response.text
    assert response.json().get("username") == USER, "Current user does not match the signed-in account"
