from conftest import BASE, USER, PASSWORD

import time

import httpx


def test_reject_invalid_json_login_credentials():
    """Reject invalid JSON login credentials."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        response = api.post(
            "/api/auth/login/json",
            json={
                "username": f"CYDIVO-QA-UNKNOWN-{int(time.time() * 1000)}",
                "password": "CYDIVO-QA-invalid-password",
            },
        )
        assert response.status_code == 401, response.text
        assert "access_token" not in response.json(), "Rejected login unexpectedly returned an access token"
