from conftest import BASE, USER, PASSWORD

import time


def sign_in(api):
    for attempt in range(3):
        response = api.post(
            "/api/auth/login/json",
            json={"username": USER, "password": PASSWORD},
        )
        if response.status_code != 429 or attempt == 2:
            break
        retry_after = float(response.headers.get("Retry-After", "1"))
        time.sleep(min(retry_after + 0.05, 2))

    assert response.status_code == 200, response.text
    token = response.json().get("access_token")
    assert token, "Login response did not contain an access token"
    return token
