from conftest import BASE, USER, PASSWORD
import httpx

from api_helpers_2 import sign_in, unique_value


def test_partial_item_update_preserves_other_fields():
    """Partially update an item without changing its other fields."""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        unique = unique_value()
        sku = f"{unique}-SKU"
        original_name = f"{unique}-Original"
        original_location = f"{unique}-Location"
        created = api.post(
            "/api/items",
            headers=headers,
            json={
                "sku": sku,
                "name": original_name,
                "quantity": 7,
                "location": original_location,
                "min_stock": 2,
            },
        )
        assert created.status_code == 201, f"Item creation failed: {created.text}"
        original = created.json()

        updated_name = f"{unique}-Updated"
        updated_location = f"{unique}-New-Location"
        response = api.patch(
            f"/api/items/{original['id']}",
            headers=headers,
            json={"name": updated_name, "location": updated_location},
        )
        assert response.status_code == 200, f"Partial update failed: {response.text}"
        item = response.json()
        assert item["name"] == updated_name, "Updated name was not returned"
        assert item["location"] == updated_location, "Updated location was not returned"
        assert item["sku"] == sku, "Partial update changed the SKU"
        assert item["quantity"] == 7, "Partial update changed the quantity"
