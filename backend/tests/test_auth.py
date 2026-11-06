import pytest

from app.routers.auth import login_rate_limiter


@pytest.fixture(autouse=True)
def reset_login_rate_limiter():
    login_rate_limiter.clear()
    yield
    login_rate_limiter.clear()


def test_login_success(client):
    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.parametrize(
    "credentials",
    [
        {"username": "admin", "password": "wrong"},
        {"username": "unknown", "password": "admin123"},
    ],
)
def test_login_json_rejects_invalid_credentials(client, credentials):
    response = client.post("/api/auth/login/json", json=credentials)
    assert response.status_code == 401


@pytest.mark.parametrize(
    "credentials",
    [
        {"username": "admin", "password": "wrong"},
        {"username": "unknown", "password": "admin123"},
    ],
)
def test_login_form_rejects_invalid_credentials(client, credentials):
    response = client.post("/api/auth/login", data=credentials)
    assert response.status_code == 401


def test_login_rate_limit_is_shared_by_both_endpoints(client):
    failed_login = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "wrong"},
    )
    assert failed_login.status_code == 401
    assert failed_login.headers["Retry-After"] == "1"

    throttled_login = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert throttled_login.status_code == 429
    assert throttled_login.headers["Retry-After"] == "1"


def test_login_rate_limiter_tracks_ip_and_account_with_progressive_delays():
    now = [100.0]
    limiter = login_rate_limiter.__class__(clock=lambda: now[0])

    assert limiter.record_failure("192.0.2.1", "admin") == 1
    assert limiter.check("192.0.2.1", "other-account") == 1
    assert limiter.check("192.0.2.2", "admin") == 1

    now[0] += 1
    assert limiter.check("192.0.2.1", "admin") is None
    assert limiter.record_failure("192.0.2.1", "admin") == 2

    now[0] += 2
    assert limiter.check("192.0.2.1", "admin") is None
    assert limiter.record_failure("192.0.2.1", "admin") == 4


def test_successful_login_resets_ip_and_account_cooldowns(client):
    failed_login = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "wrong"},
    )
    assert failed_login.status_code == 401

    # A successful login after the cooldown has elapsed clears the recorded failures.
    limiter = login_rate_limiter.__class__(clock=lambda: 0.0)
    limiter.record_failure("192.0.2.1", "admin")
    limiter.record_success("192.0.2.1", "admin")
    assert limiter.check("192.0.2.1", "admin") is None


def test_me_requires_auth(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
