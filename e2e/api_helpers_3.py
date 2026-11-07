from conftest import BASE, USER, PASSWORD


def sign_in(api):
    response = api.post(
        "/api/auth/login/json",
        json={"username": USER, "password": PASSWORD},
    )
    assert response.status_code == 200, f"Sign-in failed: {response.text}"
    return response.json()["access_token"]
