from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login, unique_value


def test_show_validation_error_for_an_item_name_that_is_too_long(page):
    """Show a validation error for an item name that is too long"""
    login(page)
    page.get_by_role("button", name="+ Add item").click()
    suffix = unique_value("LongName")
    sku = f"{suffix}-SKU"
    name = f"{suffix}-" + "X" * 140
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Description (optional)").fill("Valid description")
    page.get_by_label("Quantity").fill("4")
    page.get_by_label("Location").fill(f"{suffix}-LOC")
    page.get_by_label("Restock below").fill("2")
    page.get_by_role("button", name="Save item").click()

    expect(page.locator("form p").last, "The form should display a validation error for the oversized name").not_to_have_text("", timeout=15000)
    expect(page.get_by_text(sku, exact=True), "The invalid item should not be added to the inventory").to_have_count(0, timeout=15000)
