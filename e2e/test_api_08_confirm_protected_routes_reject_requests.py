from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers import unique_value


def test_protected_routes_reject_requests_without_a_token():
    """Confirm protected routes reject requests without a token"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        current_user = api.get("/api/auth/me")
        assert current_user.status_code == 401, current_user.text

        listing = api.get("/api/items")
        assert listing.status_code == 401, listing.text

        created = api.post(
            "/api/items",
            json={
                "sku": unique_value("NO-TOKEN-SKU"),
                "name": unique_value("NO-TOKEN-ITEM"),
                "description": unique_value("NO-TOKEN-DESCRIPTION"),
                "quantity": 2,
                "location": "QA-F-01",
                "min_stock": 1,
            },
        )
        assert created.status_code == 401, created.text
