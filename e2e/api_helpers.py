from conftest import BASE, USER, PASSWORD
import time
import uuid


def login_json(api, username=USER, password=PASSWORD):
    return api.post(
        "/api/auth/login/json",
        json={"username": username, "password": password},
    )


def demo_token(api):
    response = login_json(api)
    assert response.status_code in (200, 401), response.text
    if response.status_code == 401:
        return None
    token = response.json().get("access_token")
    assert token, "Successful login did not return an access token"
    return token


def unique_value(prefix):
    return f"CYDIVO-QA-{prefix}-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
