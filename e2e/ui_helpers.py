from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect


def login(page):
    page.goto(BASE.rstrip("/") + "/")
    page.locator("#username").fill(USER)
    page.locator("#password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    expect(page).to_have_url(BASE.rstrip("/") + "/dashboard", timeout=15000)


def create_item(page, body):
    token = page.evaluate("() => sessionStorage.getItem('storage_token')")
    assert token, "A session token should be available after signing in"
    response = page.request.post(
        BASE.rstrip("/") + "/api/items",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=body,
    )
    assert response.ok, response.text()
    return response.json()
