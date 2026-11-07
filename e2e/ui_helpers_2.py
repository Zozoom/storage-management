from conftest import BASE, USER, PASSWORD
from playwright.sync_api import expect


def login(page):
    response = page.request.post(
        f"{BASE.rstrip('/')}/api/auth/login/json",
        data={"username": USER, "password": PASSWORD},
    )
    assert response.status == 200, f"Login failed: {response.text()}"
    token = response.json()["access_token"]

    page.goto(BASE)
    page.evaluate("token => localStorage.setItem('storage_token', token)", token)
    page.goto(f"{BASE.rstrip('/')}/dashboard")
    expect(page.get_by_role("heading", name="Inventory"), "Inventory should load").to_be_visible(timeout=15000)
    expect(page.get_by_role("button", name="+ Add item"), "Inventory controls should load").to_be_visible(timeout=15000)
