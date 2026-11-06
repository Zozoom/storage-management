from conftest import BASE, USER, PASSWORD
from playwright.sync_api import expect

from ui_helpers_2 import login


def test_keep_an_incomplete_new_item_form_from_being_submitted(page):
    """Keep an incomplete new-item form from being submitted."""
    login(page)
    page.get_by_role("button", name="+ Add item").click()
    page.get_by_role("button", name="Save item").click()

    name_input = page.get_by_label("Name")
    sku_input = page.get_by_label("SKU")
    assert name_input.evaluate("el => el.validity.valueMissing"), "The empty Name field should block submission"
    assert sku_input.evaluate("el => el.validity.valueMissing"), "The empty SKU field should block submission"
    expect(page.get_by_role("heading", name="New item"), "The incomplete form should remain open").to_be_visible(timeout=15000)
