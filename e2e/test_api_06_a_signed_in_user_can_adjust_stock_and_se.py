from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import create_item, item_payload, sign_in


def test_a_signed_in_user_can_adjust_stock_and_see_the_updated_status():
    """A signed-in user can adjust stock and see the updated status."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)
        payload = item_payload("ADJUST-STOCK", quantity=1, min_stock=2)
        created = create_item(api, payload)

        increased = api.post(f"/api/items/{created['id']}/adjust", json={"delta": 1})
        assert increased.status_code == 200, f"Increasing stock failed: {increased.text}"
        assert increased.json()["quantity"] == 2, "Increased stock quantity is incorrect"
        assert increased.json()["low_stock"] is False, "Item should not be low stock at its minimum"

        decreased = api.post(f"/api/items/{created['id']}/adjust", json={"delta": -1})
        assert decreased.status_code == 200, f"Decreasing stock failed: {decreased.text}"
        assert decreased.json()["quantity"] == 1, "Decreased stock quantity is incorrect"
        assert decreased.json()["low_stock"] is True, "Item should be low stock below its minimum"
