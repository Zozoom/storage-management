from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import add_item, login, unique_value


def test_find_an_item_by_its_unique_sku(page):
    """Find an item by its unique SKU."""
    login(page)
    value = unique_value()
    name = f"{value} Item"
    sku = f"{value}-SKU"
    add_item(page, name, sku)

    search = page.get_by_role("searchbox", name="Search items")
    expect(search, "The inventory search should be visible").to_be_visible(timeout=15000)
    search.fill(sku)

    matching_row = page.locator("tbody tr").filter(has_text=sku)
    expect(matching_row, "The item matching the SKU should be shown").to_be_visible(timeout=15000)
    expect(matching_row, "The search results should include the item's name").to_contain_text(name, timeout=15000)
    expect(page.locator("tbody tr"), "Items that do not match the unique SKU should be hidden").to_have_count(1, timeout=15000)
