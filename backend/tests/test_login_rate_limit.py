from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.routers import auth as auth_router


@pytest.fixture(autouse=True)
def clear_login_attempts():
    with auth_router._login_attempts_lock:
        auth_router._login_attempts.clear()
    yield
    with auth_router._login_attempts_lock:
        auth_router._login_attempts.clear()


def make_request(ip: str):
    return SimpleNamespace(client=SimpleNamespace(host=ip))


def test_login_rate_limit_is_per_account_and_ip(monkeypatch):
    monkeypatch.setattr(auth_router, "LOGIN_IP_RATE_LIMIT", 2)
    monkeypatch.setattr(auth_router, "LOGIN_ACCOUNT_RATE_LIMIT", 1)
    request = make_request("192.0.2.1")

    auth_router._check_login_rate_limit(request, "admin")
    with pytest.raises(HTTPException) as account_error:
        auth_router._check_login_rate_limit(request, "ADMIN")
    assert account_error.value.status_code == 429
    assert account_error.value.headers["Retry-After"]

    auth_router._check_login_rate_limit(request, "clerk")
    with pytest.raises(HTTPException) as ip_error:
        auth_router._check_login_rate_limit(request, "another-user")
    assert ip_error.value.status_code == 429


def test_login_rate_limit_is_separate_for_different_ips(monkeypatch):
    monkeypatch.setattr(auth_router, "LOGIN_IP_RATE_LIMIT", 1)
    monkeypatch.setattr(auth_router, "LOGIN_ACCOUNT_RATE_LIMIT", 1)

    auth_router._check_login_rate_limit(make_request("192.0.2.1"), "admin")
    auth_router._check_login_rate_limit(make_request("192.0.2.2"), "admin")
