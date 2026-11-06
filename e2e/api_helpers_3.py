from conftest import BASE, USER, PASSWORD

import time


def sign_in(api):
    response = api.post(
        "/api/auth/login/json",
        json={"username": USER, "password": PASSWORD},
    )
    response.raise_for_status()
    api.headers["Authorization"] = f"Bearer {response.json()['access_token']}"


def unique_value():
    return f"CYDIVO-QA-{int(time.time() * 1000)}"
