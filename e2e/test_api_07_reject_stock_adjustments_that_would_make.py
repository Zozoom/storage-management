from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import item_payload, sign_in


def test_reject_stock_adjustments_that_would_make_quantity_invalid():
    """Reject stock adjustments that would make quantity invalid"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        payload = item_payload("INVALID-ADJUST", quantity=1, min_stock=0)
        created = api.post("/api/items", json=payload, headers=headers)
        assert created.status_code == 201, created.text
        item_id = created.json()["id"]

        insufficient = api.post(
            f"/api/items/{item_id}/adjust",
            json={"delta": -2},
            headers=headers,
        )
        overflow = api.post(
            f"/api/items/{item_id}/adjust",
            json={"delta": 1_000_000_000},
            headers=headers,
        )
        fetched = api.get(f"/api/items/{item_id}", headers=headers)

    assert insufficient.status_code == 400, insufficient.text
    assert overflow.status_code == 422, overflow.text
    assert fetched.status_code == 200, fetched.text
    assert fetched.json().get("quantity") == 1, "Rejected adjustments changed the item's quantity"
