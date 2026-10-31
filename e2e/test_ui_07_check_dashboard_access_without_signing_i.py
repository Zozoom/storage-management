from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login


def test_check_dashboard_access_without_signing_in(page):
    """Check dashboard access without signing in"""
    page.goto(f"{BASE}/dashboard")
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=15000)

    if not login(page):
        expect(page.get_by_text("Invalid username or password", exact=True)).to_be_visible(timeout=15000)
        return

    expect(page.get_by_role("heading", name="Inventory")).to_be_visible(timeout=15000)
    page.get_by_role("button", name="Log out").click()
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=15000)

    page.goto(f"{BASE}/dashboard")
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=15000)
