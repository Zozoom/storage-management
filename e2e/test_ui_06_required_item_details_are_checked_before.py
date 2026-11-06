from conftest import BASE, USER, PASSWORD
from ui_helpers_2 import login, unique_value

from playwright.sync_api import expect


def test_required_item_details_are_checked_before_saving(page):
    """Required item details are checked before saving."""
    login(page)
    sku = unique_value("REQUIRED-SKU")

    page.get_by_role("button", name="Add item").click()
    name_input = page.get_by_label("Name")
    page.get_by_label("SKU").fill(sku)
    page.get_by_role("button", name="Save item").click()

    assert name_input.evaluate("element => element.validity.valueMissing"), "The browser should reject saving while the required Name field is blank"
    expect(name_input, "The add-item form should remain open after required-field validation").to_be_visible(timeout=15000)
    expect(page.get_by_text(sku, exact=True), "An item with the test SKU should not be created when Name is blank").to_have_count(0, timeout=15000)
