from conftest import BASE, USER, PASSWORD
import time
import uuid


def sign_in(api):
    response = api.post(
        "/api/auth/login/json",
        json={"username": USER, "password": PASSWORD},
    )
    assert response.status_code == 200, f"Sign-in failed: {response.text}"
    token = response.json().get("access_token")
    assert isinstance(token, str) and token, "Sign-in did not return an access token"
    return token


def unique_value():
    return f"CYDIVO-QA-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
