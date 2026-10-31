from conftest import BASE, USER, PASSWORD

import httpx


def test_reject_incorrect_credentials_and_invalid_tokens_and_check_service_health():
    """Reject incorrect credentials and invalid tokens, and check service health."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        incorrect_password = api.post(
            "/api/auth/login/json",
            json={"username": "admin", "password": "incorrect-password"},
        )
        unknown_user = api.post(
            "/api/auth/login/json",
            json={"username": "CYDIVO-QA-unknown-user", "password": "any-password"},
        )
        invalid_token = api.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer not-a-valid-token"},
        )
        health = api.get("/health")

    assert incorrect_password.status_code == 401, incorrect_password.text
    assert unknown_user.status_code == 401, unknown_user.text
    assert invalid_token.status_code == 401, invalid_token.text
    assert health.status_code == 200, health.text
    assert health.json().get("status") == "ok", "Health endpoint did not report status ok"
