from conftest import BASE, USER, PASSWORD

import httpx
import time

from api_helpers_3 import sign_in


def test_require_authentication_to_read_or_change_inventory():
    """Require authentication to read or change inventory."""
    unique = f"CYDIVO-QA-{int(time.time() * 1000)}"

    # Use a fresh client for the unauthenticated requests.
    with httpx.Client(base_url=BASE, timeout=20) as api:
        listed = api.get("/api/items")
        assert listed.status_code == 401, f"Unauthenticated item listing was allowed: {listed.text}"

        created = api.post(
            "/api/items",
            json={
                "sku": unique,
                "name": unique,
                "description": "Unauthenticated API test attempt.",
                "quantity": 1,
                "location": "QA-01",
                "min_stock": 0,
            },
        )
        assert created.status_code == 401, f"Unauthenticated item creation was allowed: {created.text}"

    # Confirm the rejected create did not add the test item.
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        listed_after_attempt = api.get(
            "/api/items", headers={"Authorization": f"Bearer {token}"}
        )
        assert listed_after_attempt.status_code == 200, f"Could not verify inventory: {listed_after_attempt.text}"
        assert all(item["sku"] != unique for item in listed_after_attempt.json()), "Unauthenticated create added the test item"
