from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login


def test_dashboard_remains_private_when_signed_out(page):
    """Keep the dashboard private when signed out."""
    dashboard_url = f"{BASE.rstrip('/')}/dashboard"

    page.goto(dashboard_url)
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=15000)
    expect(page.get_by_role("heading", name="Inventory")).not_to_be_visible(timeout=15000)
    expect(page).to_have_url(f"{BASE.rstrip('/')}/", timeout=15000)

    login(page)
    page.get_by_role("button", name="Log out").click()
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=15000)

    page.goto(dashboard_url)
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=15000)
    expect(page.get_by_role("heading", name="Inventory")).not_to_be_visible(timeout=15000)
    expect(page).to_have_url(f"{BASE.rstrip('/')}/", timeout=15000)
