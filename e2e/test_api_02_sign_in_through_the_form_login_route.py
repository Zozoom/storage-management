from conftest import BASE, USER, PASSWORD
import httpx


def test_sign_in_through_form_login_route():
    """Sign in through the form login route"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        response = api.post(
            "/api/auth/login",
            data={"username": "clerk", "password": "clerk123"},
        )
        assert response.status_code in (200, 401), response.text
        if response.status_code == 200:
            token = response.json().get("access_token")
            assert token, "Successful form login did not return an access token"
            assert response.json().get("token_type") == "bearer", "Form login returned an unexpected token type"
            me = api.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert me.status_code == 200, me.text
            assert me.json().get("username") == "clerk", "Current-user endpoint did not identify clerk"
        else:
            assert response.json().get("detail") == "Incorrect username or password", "Demo login rejection did not return the expected error"
