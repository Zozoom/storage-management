from conftest import BASE, USER, PASSWORD
import httpx


def test_show_error_for_an_incorrect_password():
    """Show the error for an incorrect password"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        response = api.post(
            "/api/auth/login/json",
            json={"username": "admin", "password": "CYDIVO-QA-incorrect-password"},
        )
        assert response.status_code == 401, response.text
        body = response.json()
        assert body.get("detail") == "Incorrect username or password", "Incorrect-password response did not return the login failure message"
        assert "access_token" not in body, "Failed login unexpectedly returned an access token"
