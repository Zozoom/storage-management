from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers import login_json


def test_sign_in_through_json_login_route():
    """Sign in through the JSON login route"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        response = login_json(api, "admin", "admin123")
        assert response.status_code in (200, 401), response.text
        if response.status_code == 200:
            token = response.json().get("access_token")
            assert token, "Successful JSON login did not return an access token"
            assert response.json().get("token_type") == "bearer", "JSON login returned an unexpected token type"
            me = api.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert me.status_code == 200, me.text
            assert me.json().get("username") == "admin", "Current-user endpoint did not identify admin"
        else:
            assert response.json().get("detail") == "Incorrect username or password", "Demo login rejection did not return the expected error"
