from conftest import BASE, USER, PASSWORD

import httpx


def test_reject_invalid_credentials_on_both_login_routes():
    """Reject invalid credentials on both login routes"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        json_response = api.post(
            "/api/auth/login/json",
            json={"username": USER, "password": f"{PASSWORD}-incorrect"},
        )
        form_response = api.post(
            "/api/auth/login",
            data={"username": USER, "password": f"{PASSWORD}-incorrect"},
        )

    assert json_response.status_code == 401, json_response.text
    assert form_response.status_code == 401, form_response.text
    assert json_response.json() == form_response.json(), "Login routes returned different invalid-credentials responses"
    assert "access_token" not in json_response.json(), "Invalid credentials unexpectedly returned a token"
    assert "access_token" not in form_response.json(), "Invalid credentials unexpectedly returned a token"
