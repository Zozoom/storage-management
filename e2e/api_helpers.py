from conftest import BASE, USER, PASSWORD

import time


def unique_value(prefix: str) -> str:
    return f"CYDIVO-QA-{prefix}-{int(time.time() * 1000)}"


def sign_in(api):
    response = api.post(
        "/api/auth/login/json",
        json={"username": USER, "password": PASSWORD},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json().get("access_token")
    assert token, f"Login response did not include an access token: {response.text}"
    return token
