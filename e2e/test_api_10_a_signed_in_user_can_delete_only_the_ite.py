from conftest import BASE, USER, PASSWORD

import time

import httpx

from api_helpers_3 import sign_in


def test_signed_in_user_can_delete_only_the_item_created_for_this_test():
    """A signed-in user can delete only the item created for this test."""
    unique = f"CYDIVO-QA-{time.time_ns()}"
    item_body = {
        "sku": f"{unique}-DELETE",
        "name": f"{unique} delete-test item",
        "quantity": 3,
        "location": "A-01",
        "min_stock": 1,
    }

    with httpx.Client(base_url=BASE, timeout=20) as api:
        sign_in(api)

        create_response = api.post("/api/items", json=item_body)
        assert create_response.status_code == 201, create_response.text
        item_id = create_response.json()["id"]

        delete_response = api.delete(f"/api/items/{item_id}")
        assert delete_response.status_code == 204, delete_response.text

        retrieval_response = api.get(f"/api/items/{item_id}")
        assert retrieval_response.status_code == 404, retrieval_response.text
