from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import create_item, item_payload, sign_in


def test_stock_cannot_be_adjusted_beyond_the_supported_maximum():
    """Stock cannot be adjusted beyond the supported maximum."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        maximum = 9_223_372_036_854_775_807
        created = create_item(api, item_payload("MAX-STOCK", quantity=maximum, min_stock=0))

        adjustment = api.post(f"/api/items/{created['id']}/adjust", json={"delta": 1})
        assert adjustment.status_code == 400, f"Overflowing stock adjustment was not rejected with 400: {adjustment.text}"
        assert adjustment.json().get("detail") == "Quantity exceeds maximum allowed value", "Overflow response detail was unexpected"

        readback = api.get(f"/api/items/{created['id']}")
        assert readback.status_code == 200, f"Reading the item after rejected adjustment failed: {readback.text}"
        assert readback.json()["quantity"] == maximum, "Rejected adjustment changed the item's quantity"
