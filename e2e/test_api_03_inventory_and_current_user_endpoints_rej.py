from conftest import BASE, USER, PASSWORD

import httpx


def test_inventory_and_current_user_endpoints_reject_requests_without_a_session():
    """Inventory and current-user endpoints reject requests without a session."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        items = api.get("/api/items")
        me = api.get("/api/auth/me")

        assert items.status_code == 401, f"Unauthenticated inventory request was not rejected: {items.text}"
        assert me.status_code == 401, f"Unauthenticated current-user request was not rejected: {me.text}"
        assert isinstance(items.json(), dict) and "detail" in items.json(), "Inventory response disclosed data instead of an authentication error"
        assert isinstance(me.json(), dict) and "detail" in me.json(), "Current-user response disclosed user details"
        assert "storage_session" not in api.cookies, "Fresh client unexpectedly has a session cookie"
