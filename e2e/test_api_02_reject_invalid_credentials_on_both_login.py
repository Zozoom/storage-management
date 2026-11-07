from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import unique_value


def test_reject_invalid_credentials_on_both_login_routes():
    """Reject invalid credentials on both login routes."""
    username = unique_value("INVALID-USER")
    password = unique_value("INVALID-PASSWORD")

    with httpx.Client(base_url=BASE, timeout=20) as api:
        json_response = api.post(
            "/api/auth/login/json",
            json={"username": username, "password": password},
        )
        assert json_response.status_code == 401, f"JSON login should reject invalid credentials: {json_response.text}"
        assert "access_token" not in json_response.json(), f"JSON login issued a token for invalid credentials: {json_response.text}"

        form_response = api.post(
            "/api/auth/login",
            data={"username": username, "password": password},
        )
        assert form_response.status_code == 401, f"Form login should reject invalid credentials: {form_response.text}"
        assert "access_token" not in form_response.json(), f"Form login issued a token for invalid credentials: {form_response.text}"
