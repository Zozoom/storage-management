from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import item_payload, sign_in


def test_delete_only_the_item_created_for_this_request():
    """Delete only the item created for this request"""
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = {"Authorization": f"Bearer {token}"}
        created = api.post(
            "/api/items",
            json=item_payload("DELETE"),
            headers=headers,
        )
        assert created.status_code == 201, created.text
        item_id = created.json()["id"]

        deleted = api.delete(f"/api/items/{item_id}", headers=headers)
        fetched = api.get(f"/api/items/{item_id}", headers=headers)

    assert deleted.status_code == 204, deleted.text
    assert fetched.status_code == 404, fetched.text
