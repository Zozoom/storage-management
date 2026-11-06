from conftest import BASE, USER, PASSWORD


def sign_in(api):
    response = api.post(
        "/api/auth/login/json",
        json={"username": USER, "password": PASSWORD},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    api.headers.update({"Authorization": f"Bearer {token}"})
