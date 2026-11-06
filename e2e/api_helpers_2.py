from conftest import BASE, USER, PASSWORD

import uuid


def sign_in(api):
    response = api.post(
        "/api/auth/login/json",
        json={"username": USER, "password": PASSWORD},
    )
    assert response.status_code == 200, f"Sign-in failed: {response.text}"
    token = response.json().get("access_token")
    assert token, "Sign-in response did not include an access token"
    api.headers["Authorization"] = f"Bearer {token}"
    return token


def unique_value(prefix):
    return f"CYDIVO-QA-{prefix}-{uuid.uuid4().hex}"


def unique_item(quantity=0, min_stock=5):
    return {
        "sku": unique_value("SKU"),
        "name": unique_value("ITEM"),
        "description": "CYDIVO-QA item created by an API test",
        "quantity": quantity,
        "location": "QA-A-01",
        "min_stock": min_stock,
    }
