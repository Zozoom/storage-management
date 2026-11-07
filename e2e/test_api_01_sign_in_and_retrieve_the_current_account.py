from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import sign_in


def test_sign_in_and_retrieve_current_account():
    """Sign in and retrieve the current account."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        response = api.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, f"Could not retrieve current account: {response.text}"
        assert response.json().get("username") == USER, f"Current account did not identify the configured administrator: {response.text}"
