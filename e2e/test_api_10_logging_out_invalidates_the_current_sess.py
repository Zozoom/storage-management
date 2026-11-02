from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import sign_in


def test_logging_out_invalidates_the_current_session():
    """Logging out invalidates the current session."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        logout = api.post("/api/auth/logout")
        assert logout.status_code == 204, f"Logout failed: {logout.text}"
        assert "storage_session" not in api.cookies, "Logout did not clear the session cookie"
        clear_cookie = " ".join(logout.headers.get_list("set-cookie")).lower()
        assert "storage_session" in clear_cookie and "max-age=0" in clear_cookie, "Logout response did not expire the session cookie"

        me = api.get("/api/auth/me")
        assert me.status_code == 401, f"Session remained authenticated after logout: {me.text}"
