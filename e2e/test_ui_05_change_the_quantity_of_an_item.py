from conftest import BASE, USER, PASSWORD
from playwright.sync_api import expect

from ui_helpers_2 import add_item, login, unique_value


def test_change_the_quantity_of_an_item(page):
    """Change the quantity of an item."""
    login(page)
    name = unique_value("Increase")
    sku = unique_value("SKU-Increase")
    row = add_item(page, name, sku, 1)

    row.get_by_role("button", name=f"Increase {name}").click()

    expect(row.get_by_text("2", exact=True), "The item's quantity should increase to 2").to_be_visible(timeout=15000)
    expect(row, "The created item should remain in the inventory").to_be_visible(timeout=15000)
