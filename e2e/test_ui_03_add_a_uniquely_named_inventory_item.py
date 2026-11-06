from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import add_item, login, unique_value


def test_add_a_uniquely_named_inventory_item(page):
    """Add a uniquely named inventory item."""
    login(page)
    value = unique_value()
    name = f"{value} Item"
    sku = f"{value}-SKU"
    description = f"{value} description"
    add_item(page, name, sku, quantity="8", location="A-01", min_stock="5", description=description)

    item_row = page.locator("tbody tr").filter(has_text=sku)
    expect(item_row, "The newly created item should appear in inventory").to_be_visible(timeout=15000)
    expect(item_row, "The item should show its submitted name").to_contain_text(name, timeout=15000)
    expect(item_row, "The item should show its submitted SKU").to_contain_text(sku, timeout=15000)
    expect(item_row, "The item should show its submitted description").to_contain_text(description, timeout=15000)
    expect(item_row, "The item should show its submitted location").to_contain_text("A-01", timeout=15000)
    expect(item_row, "The item should show its submitted quantity").to_contain_text("8", timeout=15000)
    expect(item_row, "Stock above the threshold should be marked in stock").to_contain_text("In stock", timeout=15000)
