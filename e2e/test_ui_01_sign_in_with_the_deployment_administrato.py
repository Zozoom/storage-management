from conftest import BASE, USER, PASSWORD
from playwright.sync_api import expect

from ui_helpers import login


def test_sign_in_with_deployment_administrator_account(page):
    """Sign in with the deployment administrator account."""
    page.goto(BASE)
    expect(page.locator("input").nth(0), "Username field should start blank").to_have_value("", timeout=15000)
    expect(page.locator("input").nth(1), "Password field should start blank").to_have_value("", timeout=15000)

    login(page)
    expect(page.get_by_role("heading", name="Inventory"), "Inventory dashboard should open").to_be_visible(timeout=15000)
