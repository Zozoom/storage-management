from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import sign_in


def test_json_login_and_current_user():
    """Sign in with JSON credentials and retrieve the current user."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        response = api.post(
            "/api/auth/login/json",
            json={"username": USER, "password": PASSWORD},
        )
        assert response.status_code == 200, response.text
        token = response.json().get("access_token")
        assert token, "Login response did not contain an access token"

        current_user = api.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert current_user.status_code == 200, current_user.text
        assert current_user.json().get("username") == USER, "Current user does not match the signed-in account"
