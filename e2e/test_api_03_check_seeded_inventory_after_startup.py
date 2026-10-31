from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers import demo_token


def test_check_seeded_inventory_after_startup():
    """Check seeded inventory after startup"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = demo_token(api)
        if token is None:
            response = api.get("/api/items")
            assert response.status_code == 401, response.text
            return

        response = api.get("/api/items", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        items = response.json()
        by_sku = {item["sku"]: item for item in items}
        assert "WDG-001" in by_sku, "Seeded Widget was not found"
        assert by_sku["WDG-001"]["name"] == "Widget", "Seeded Widget has an unexpected name"
        assert "BOLT-M8" in by_sku, "Seeded M8 Bolt was not found"
        assert by_sku["BOLT-M8"]["name"] == "M8 Bolt", "Seeded bolt has an unexpected name"
        assert "BOX-S" in by_sku, "Seeded Small Box was not found"
        assert by_sku["BOX-S"]["name"] == "Small Box", "Seeded box has an unexpected name"
        assert by_sku["BOX-S"]["low_stock"] is True, "Seeded Small Box was not marked low stock"
