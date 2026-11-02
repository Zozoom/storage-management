from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import unique_value


def test_both_login_endpoints_reject_invalid_credentials():
    """Both login endpoints reject invalid credentials."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        json_login = api.post(
            "/api/auth/login/json",
            json={"username": unique_value("NONEXISTENT-USER"), "password": unique_value("BAD-PASSWORD")},
        )
        form_login = api.post(
            "/api/auth/login",
            data={"username": USER, "password": unique_value("BAD-PASSWORD")},
        )

        assert json_login.status_code == 401, f"JSON login accepted invalid credentials: {json_login.text}"
        assert form_login.status_code == 401, f"Form login accepted invalid credentials: {form_login.text}"
        assert json_login.json() == form_login.json(), "Login endpoints returned different invalid-credential responses"
        assert json_login.json().get("detail") == "Incorrect username or password", "Invalid-credential response detail was unexpected"
        assert "storage_session" not in api.cookies, "Invalid login issued an authenticated session cookie"
        assert not json_login.headers.get_list("set-cookie"), "JSON login issued a cookie for invalid credentials"
        assert not form_login.headers.get_list("set-cookie"), "Form login issued a cookie for invalid credentials"
