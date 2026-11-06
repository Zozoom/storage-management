from conftest import BASE, USER, PASSWORD
import time

import httpx


def test_both_sign_in_routes_reject_unknown_users_and_incorrect_passwords():
    """Both sign-in routes reject unknown users and incorrect passwords."""
    username = f"CYDIVO-QA-UNKNOWN-{int(time.time() * 1000)}"
    password = f"CYDIVO-QA-password-{int(time.time() * 1000)}"

    with httpx.Client(base_url=BASE, timeout=20) as api:
        json_response = api.post(
            "/api/auth/login/json",
            json={"username": username, "password": password},
        )
        form_response = api.post(
            "/api/auth/login",
            data={"username": username, "password": password},
        )

    assert json_response.status_code == 401, json_response.text
    assert form_response.status_code == 401, form_response.text
    assert json_response.json().get("detail") == "Incorrect username or password", json_response.text
    assert form_response.json().get("detail") == "Incorrect username or password", form_response.text
    assert json_response.json() == form_response.json(), "Both sign-in routes should return the same invalid-credentials response"
    assert "access_token" not in json_response.json(), json_response.text
    assert "access_token" not in form_response.json(), form_response.text
