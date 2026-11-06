from conftest import BASE, USER, PASSWORD

import uuid


def sign_in(api):
    response = api.post(
        "/api/auth/login/json",
        json={"username": USER, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    token = response.json().get("access_token")
    assert token, "Login response did not include an access token"
    return token


def unique_value(prefix):
    return f"CYDIVO-QA-{prefix}-{uuid.uuid4().hex}"


def item_payload(prefix, *, quantity=6, min_stock=2, description="Test inventory item"):
    value = unique_value(prefix)
    return {
        "sku": f"{value}-SKU",
        "name": f"{value} item",
        "description": description,
        "quantity": quantity,
        "location": f"{value}-LOC",
        "min_stock": min_stock,
    }
