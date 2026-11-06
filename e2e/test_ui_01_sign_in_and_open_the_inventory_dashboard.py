from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login


def test_sign_in_and_open_inventory_dashboard(page):
    """Sign in and open the inventory dashboard"""
    login(page)
    expect(page.get_by_role("heading", name="Inventory"), "The Inventory dashboard should appear after signing in").to_be_visible(timeout=15000)

    page.reload()
    expect(page.get_by_role("heading", name="Inventory"), "The signed-in session should remain after refreshing").to_be_visible(timeout=15000)
