from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login


def test_sign_in_with_an_account_configured_for_this_deployment(page):
    """Sign in with an account configured for this deployment."""
    login(page)
    expect(page.get_by_role("button", name="Log out"), "The signed-in session should be visible").to_be_visible(timeout=15000)
