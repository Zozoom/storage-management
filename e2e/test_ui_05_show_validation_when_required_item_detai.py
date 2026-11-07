from conftest import BASE, USER, PASSWORD
import time

from playwright.sync_api import expect
from ui_helpers_2 import login


def test_show_validation_when_required_item_details_are_missing(page):
    """Show validation when required item details are missing."""
    login(page)
    sku = f"CYDIVO-QA-SKU-{int(time.time() * 1000)}"

    page.get_by_role("button", name="+ Add item").click()
    name_input = page.get_by_label("Name")
    name_input.fill("")
    page.get_by_label("SKU").fill(sku)
    page.get_by_role("button", name="Save item").click()

    assert name_input.evaluate("element => element.validity.valueMissing"), "An empty required Name field should block submission"
    page.get_by_placeholder("Search by name, SKU or location…").fill(sku)
    expect(page.get_by_text("No items found."), "The invalid submission should not add an item").to_be_visible(timeout=15000)
