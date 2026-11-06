from conftest import BASE, USER, PASSWORD


def sign_in(api):
    response = api.post(
        "/api/auth/login/json",
        json={"username": USER, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    token = response.json().get("access_token")
    assert token, "Successful sign-in should return an access token"
    return token
