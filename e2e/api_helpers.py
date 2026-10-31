from conftest import BASE, USER, PASSWORD

import uuid


def sign_in(api, username=USER, password=PASSWORD):
    response = api.post(
        "/api/auth/login/json",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data.get("access_token"), "Login response did not include an access token"
    assert data.get("token_type") == "bearer", "Login response did not identify a bearer token"
    return data["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def unique_item(**overrides):
    suffix = uuid.uuid4().hex
    item = {
        "sku": f"CYDIVO-QA-{suffix}",
        "name": f"CYDIVO QA item {suffix}",
        "description": f"CYDIVO QA test record {suffix}",
        "quantity": 8,
        "location": f"QA-{suffix[:8]}",
        "min_stock": 5,
    }
    item.update(overrides)
    return item
