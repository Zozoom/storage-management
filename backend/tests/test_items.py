def test_list_items(client, auth_headers):
    response = client.get("/api/items", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["sku"] == "TEST-1"
    assert items[0]["low_stock"] is False


def test_list_items_unauthorized(client):
    response = client.get("/api/items")
    assert response.status_code == 401


def test_create_item(client, auth_headers):
    response = client.post(
        "/api/items",
        headers=auth_headers,
        json={
            "sku": "NEW-1",
            "name": "New Thing",
            "quantity": 5,
            "location": "A-99",
            "min_stock": 2,
        },
    )
    assert response.status_code == 201
    assert response.json()["sku"] == "NEW-1"


def test_adjust_stock(client, auth_headers):
    listed = client.get("/api/items", headers=auth_headers).json()
    item_id = listed[0]["id"]

    response = client.post(
        f"/api/items/{item_id}/adjust",
        headers=auth_headers,
        json={"delta": -3},
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 7


def test_adjust_stock_insufficient(client, auth_headers):
    listed = client.get("/api/items", headers=auth_headers).json()
    item_id = listed[0]["id"]

    response = client.post(
        f"/api/items/{item_id}/adjust",
        headers=auth_headers,
        json={"delta": -999},
    )
    assert response.status_code == 400


def test_delete_item(client, auth_headers):
    listed = client.get("/api/items", headers=auth_headers).json()
    item_id = listed[0]["id"]

    response = client.delete(f"/api/items/{item_id}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get("/api/items", headers=auth_headers).json() == []
