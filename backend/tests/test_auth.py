import pytest

from app.routers import auth as auth_router


@pytest.fixture(autouse=True)
def clear_login_failures():
    with auth_router._login_failures_lock:
        auth_router._login_failures.clear()
    yield
    with auth_router._login_failures_lock:
        auth_router._login_failures.clear()


@pytest.fixture
def disable_login_delay(monkeypatch):
    async def no_delay(_seconds):
        pass

    monkeypatch.setattr(auth_router.asyncio, "sleep", no_delay)
    monkeypatch.setattr(auth_router, "PROGRESSIVE_DELAY_BASE_SECONDS", 0)


def test_login_success(client):
    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure(client, disable_login_delay):
    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    "path,payload",
    [
        (
            "/api/auth/login/json",
            {"json": {"username": "admin", "password": "wrong"}},
        ),
        (
            "/api/auth/login",
            {"data": {"username": "admin", "password": "wrong"}},
        ),
    ],
)
def test_both_login_routes_throttle_repeated_failures(
    client, disable_login_delay, monkeypatch, path, payload
):
    monkeypatch.setattr(auth_router, "LOGIN_FAILURE_LIMIT", 2)

    assert client.post(path, **payload).status_code == 401
    assert client.post(path, **payload).status_code == 401

    response = client.post(path, **payload)
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0


def test_throttling_covers_ip_and_account_scopes(monkeypatch):
    monkeypatch.setattr(auth_router, "LOGIN_FAILURE_LIMIT", 2)
    monkeypatch.setattr(auth_router, "PROGRESSIVE_DELAY_BASE_SECONDS", 0)
    auth_router._record_login_failure("192.0.2.1", "admin")
    auth_router._record_login_failure("192.0.2.1", "admin")

    assert auth_router._throttle_retry_after("192.0.2.2", "admin") is not None
    assert auth_router._throttle_retry_after("192.0.2.1", "clerk") is not None


def test_demo_account_login_is_disabled_in_production(
    client, disable_login_delay, monkeypatch
):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("VERCEL_ENV", "development")
    monkeypatch.setenv("NODE_ENV", "development")

    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 401


def test_me_requires_auth(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
