def test_login_success(client):
    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_lets_anyone_in(client):
    for body in ({"username": "admin", "password": "wrong"}, {"username": "", "password": ""}):
        token = client.post("/api/auth/login/json", json=body).json()["access_token"]
        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.json()["username"] == "admin"


def test_me_requires_auth(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
