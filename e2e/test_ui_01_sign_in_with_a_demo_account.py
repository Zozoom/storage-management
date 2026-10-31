from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login


def test_sign_in_with_a_demo_account(page):
    """Sign in with a demo account"""
    if login(page):
        expect(page.get_by_role("heading", name="Inventory")).to_be_visible(timeout=15000)
    else:
        expect(page.get_by_text("Invalid username or password", exact=True)).to_be_visible(timeout=15000)
