from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login


def test_valid_account_can_sign_in_and_reach_inventory(page):
    """A valid account can sign in and reach the inventory."""
    login(page)

    expect(page.get_by_role("heading", name="Inventory")).to_be_visible(timeout=15000)
    assert not page.evaluate(
        "() => Object.keys(localStorage).some(key => key.toLowerCase().includes('token'))"
    ), "A session token should not be stored in local storage"
