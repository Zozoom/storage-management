from conftest import BASE, USER, PASSWORD

import httpx

from api_helpers import auth_headers, sign_in, unique_item


def test_delete_an_item_and_verify_it_is_gone():
    """Delete an item and verify it is gone."""
    item = unique_item()
    with httpx.Client(base_url=BASE, timeout=20) as api:
        token = sign_in(api)
        headers = auth_headers(token)
        created = api.post("/api/items", json=item, headers=headers)
        assert created.status_code == 201, created.text
        item_id = created.json()["id"]

        deleted = api.delete(f"/api/items/{item_id}", headers=headers)
        missing = api.get(f"/api/items/{item_id}", headers=headers)

    assert deleted.status_code == 204, deleted.text
    assert missing.status_code == 404, missing.text
