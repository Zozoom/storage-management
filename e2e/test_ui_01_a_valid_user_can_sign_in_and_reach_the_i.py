from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login


def test_valid_user_can_sign_in_and_reach_inventory(page):
    """A valid user can sign in and reach the inventory."""
    login(page)
    assert page.url == BASE.rstrip("/") + "/dashboard", "Successful sign-in should open the dashboard"
    inventory = page.locator("table").or_(page.get_by_text("No items found.", exact=True))
    expect(inventory, "The inventory list should be displayed").to_be_visible(timeout=15000)
