from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_value


def test_find_an_item_by_its_unique_sku(page):
    """Find an item by its unique SKU"""
    login(page)
    suffix = unique_value("Search")
    sku = f"{suffix}-SKU"
    create_item(page, name=f"{suffix} Search Item", sku=sku, quantity=4, location=f"{suffix}-LOC", min_stock=2)

    page.get_by_label("Search items").fill(sku)
    row = page.get_by_role("row").filter(has_text=sku)
    expect(row, "The item matching the unique SKU should remain visible in search results").to_be_visible(timeout=15000)
