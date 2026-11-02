import pytest


SESSION_COOKIE = "storage_session"


def test_login_sets_secure_http_only_session_cookie(client):
    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Login successful"}
    assert "access_token" not in response.json()

    cookie = response.headers["set-cookie"]
    assert f"{SESSION_COOKIE}=" in cookie
    assert "httponly" in cookie.lower()
    assert "secure" in cookie.lower()
    assert "samesite=lax" in cookie.lower()
    assert response.headers["cache-control"] == "no-store"

    current_user = client.get(
        "/api/auth/me",
        cookies={SESSION_COOKIE: response.cookies[SESSION_COOKIE]},
    )
    assert current_user.status_code == 200
    assert current_user.json()["username"] == "admin"


@pytest.mark.parametrize(
    ("path", "credentials"),
    [
        ("/api/auth/login/json", {"json": {"username": "admin", "password": "wrong"}}),
        ("/api/auth/login/json", {"json": {"username": "unknown", "password": "admin123"}}),
        ("/api/auth/login", {"data": {"username": "admin", "password": "wrong"}}),
        ("/api/auth/login", {"data": {"username": "unknown", "password": "admin123"}}),
    ],
)
def test_login_rejects_invalid_credentials(client, path, credentials):
    response = client.post(path, **credentials)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_login_rate_limited_per_ip(client, monkeypatch):
    from collections import OrderedDict
    from threading import Lock

    import app.main as main

    monkeypatch.setattr(main, "_login_attempts", OrderedDict())
    monkeypatch.setattr(main, "_login_attempts_lock", Lock())

    for attempt in range(main._LOGIN_RATE_LIMIT):
        response = client.post(
            "/api/auth/login/json",
            json={"username": f"unknown-{attempt}", "password": "wrong"},
        )
        assert response.status_code == 401

    response = client.post(
        "/api/auth/login/json",
        json={"username": "another-unknown", "password": "wrong"},
    )
    assert response.status_code == 429
    assert response.headers["retry-after"]


def test_repeated_account_failures_trigger_cooldown(client):
    username = "cooldown-test-account"
    for _ in range(5):
        response = client.post(
            "/api/auth/login/json",
            json={"username": username, "password": "wrong"},
        )
        assert response.status_code == 401

    response = client.post(
        "/api/auth/login/json",
        json={"username": username, "password": "wrong"},
    )
    assert response.status_code == 429
    assert response.headers["retry-after"] == "1"


def test_me_requires_auth(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_session_cookie(client, auth_cookies):
    response = client.get("/api/auth/me", cookies=auth_cookies)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_logout_clears_session_cookie(client, auth_cookies):
    response = client.post("/api/auth/logout", cookies=auth_cookies)
    assert response.status_code == 204
    assert "max-age=0" in response.headers["set-cookie"].lower()
    assert "httponly" in response.headers["set-cookie"].lower()
    assert "secure" in response.headers["set-cookie"].lower()
