from conftest import BASE, USER, PASSWORD

import time


def unique_value(tag):
    return f"CYDIVO-QA-{tag}-{time.time_ns()}"


def item_payload(tag, **overrides):
    payload = {
        "sku": unique_value(f"{tag}-SKU"),
        "name": unique_value(f"{tag}-NAME"),
        "description": f"Created by automated test {tag}",
        "quantity": 4,
        "location": "QA-A-01",
        "min_stock": 2,
    }
    payload.update(overrides)
    return payload


def sign_in(api):
    response = api.post(
        "/api/auth/login/json",
        json={"username": USER, "password": PASSWORD},
    )
    assert response.status_code == 200, f"Sign-in failed: {response.text}"
    assert "storage_session" in api.cookies, "Sign-in did not set the session cookie"
    return response


def create_item(api, payload):
    response = api.post("/api/items", json=payload)
    assert response.status_code == 201, f"Item creation failed: {response.text}"
    return response.json()
