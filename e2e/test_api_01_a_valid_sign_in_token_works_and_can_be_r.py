from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers import sign_in


def test_valid_sign_in_token_can_be_revoked_by_logging_out():
    """A valid sign-in token works and can be revoked by logging out."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}

        me_response = api.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200, me_response.text
        assert me_response.json().get("username") == USER, me_response.text

        logout_response = api.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 204, logout_response.text

        revoked_response = api.get("/api/auth/me", headers=headers)
        assert revoked_response.status_code == 401, revoked_response.text
