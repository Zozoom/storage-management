from conftest import BASE, USER, PASSWORD
import time

import httpx

from api_helpers import sign_in


def test_signed_in_user_can_create_item_and_find_it_in_inventory():
    """A signed-in user can create an item and find it in the inventory list."""
    unique = f"CYDIVO-QA-{int(time.time() * 1000)}"
    item = {
        "sku": f"{unique}-SKU",
        "name": f"{unique}-Item",
        "description": f"Created by automated test {unique}",
        "quantity": 2,
        "location": f"QA-{unique[-6:]}",
        "min_stock": 5,
    }

    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}

        create_response = api.post("/api/items", headers=headers, json=item)
        assert create_response.status_code == 201, create_response.text
        created = create_response.json()
        for field in ("sku", "name", "description", "quantity", "location", "min_stock"):
            assert created.get(field) == item[field], f"Created item {field} should match the submitted value: {create_response.text}"
        assert created.get("low_stock") is True, create_response.text

        list_response = api.get("/api/items", headers=headers)
        assert list_response.status_code == 200, list_response.text
        listed = next(
            (entry for entry in list_response.json() if entry.get("sku") == item["sku"]),
            None,
        )
        assert listed is not None, "The created item should appear in the inventory list"
        assert listed.get("low_stock") is True, "The listed item should be flagged as low stock"
