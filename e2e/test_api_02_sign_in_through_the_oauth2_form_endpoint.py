from conftest import BASE, USER, PASSWORD

import httpx


def test_oauth2_form_login():
    """Sign in through the OAuth2 form endpoint."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        response = api.post(
            "/api/auth/login",
            data={"username": USER, "password": PASSWORD},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body.get("access_token"), "Form login response did not contain an access token"
        assert body.get("token_type") == "bearer", "Form login did not return bearer token type"
