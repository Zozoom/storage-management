from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_value


def test_create_item_and_find_it_using_search(page):
    """Create an item and find it using search."""
    login(page)
    suffix = unique_value("CYDIVO-QA")
    name = f"Searchable item {suffix}"
    sku = f"SKU-{suffix}"
    location = f"LOC-{suffix}"

    create_item(page, name, sku, location, quantity=7, min_stock=2)
    search = page.get_by_label("Search items")

    search.fill(sku)
    expect(page.get_by_text(name, exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_text(sku, exact=True)).to_be_visible(timeout=15000)

    search.fill(location)
    expect(page.get_by_text(name, exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_text(location, exact=True)).to_be_visible(timeout=15000)
