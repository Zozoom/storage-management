from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_value


def test_add_a_uniquely_named_item_to_inventory(page):
    """Add a uniquely named item to inventory"""
    login(page)
    suffix = unique_value("NewItem")
    name = f"{suffix} Shipping Box"
    sku = f"{suffix}-SKU"
    location = f"{suffix}-LOC"
    create_item(page, name=name, sku=sku, quantity=4, location=location, min_stock=2, description=f"{suffix} description")

    expect(page.get_by_role("button", name="+ Add item"), "The add-item form should close after saving").to_be_visible(timeout=15000)
    row = page.get_by_role("row").filter(has_text=sku)
    expect(row, "The newly created item should appear in the inventory").to_be_visible(timeout=15000)
    expect(row, "The item should show the entered name, location, description, and quantity").to_contain_text(name, timeout=15000)
    expect(row, "The item should show its unique location").to_contain_text(location, timeout=15000)
    expect(row, "The item should show its description").to_contain_text(f"{suffix} description", timeout=15000)
    expect(row, "The item should show quantity 4").to_contain_text("4", timeout=15000)
