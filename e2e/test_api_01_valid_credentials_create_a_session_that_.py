from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import sign_in


def test_valid_credentials_create_a_session_that_identifies_the_signed_in_user():
    """Valid credentials create a session that identifies the signed-in user."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        response = api.post(
            "/api/auth/login/json",
            json={"username": USER, "password": PASSWORD},
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        cookie = api.cookies.get("storage_session")
        assert cookie, "Login did not set the storage_session cookie"
        set_cookie = " ".join(response.headers.get_list("set-cookie")).lower()
        assert "secure" in set_cookie, "Session cookie is not Secure"
        assert "httponly" in set_cookie, "Session cookie is not HttpOnly"
        assert "samesite=lax" in set_cookie, "Session cookie does not use SameSite=Lax"

        me = api.get("/api/auth/me")
        assert me.status_code == 200, f"Authenticated current-user request failed: {me.text}"
        assert me.json().get("username") == USER, "Current-user response has the wrong username"
