from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login


def test_log_out_and_return_to_the_sign_in_page(page):
    """Log out and return to the sign-in page"""
    login(page)
    page.get_by_role("button", name="Log out").click()
    expect(page.get_by_role("heading", name="Welcome back"), "Logging out should return to the sign-in page").to_be_visible(timeout=15000)
    expect(page.get_by_role("heading", name="Inventory"), "The dashboard should no longer be visible after logging out").to_have_count(0, timeout=15000)
