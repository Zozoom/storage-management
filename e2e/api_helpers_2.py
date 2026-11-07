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
    assert token, "Sign-in response did not include an access token"
    api.headers["Authorization"] = f"Bearer {token}"


def unique_value(prefix):
    return f"CYDIVO-QA-{prefix}-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
