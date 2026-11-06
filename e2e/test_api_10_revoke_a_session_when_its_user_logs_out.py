from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import sign_in


def test_revoke_a_session_when_its_user_logs_out():
    """Revoke a session when its user logs out"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        logout = api.post("/api/auth/logout", headers=headers)
        current_user = api.get("/api/auth/me", headers=headers)

    assert logout.status_code == 204, logout.text
    assert current_user.status_code == 401, current_user.text
