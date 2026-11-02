from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import add_item, login, unique_value


def test_search_finds_uniquely_created_item_by_its_sku(page):
    """Search finds a uniquely created item by its SKU."""
    login(page)
    suffix = unique_value()
    name = f"QA Search Item {suffix}"
    sku = f"QA-UI-{suffix}"
    add_item(page, name, sku, location=f"QA-SHELF-{suffix}")

    page.get_by_label("Search items").fill(sku)
    expect(page.get_by_role("row").filter(has_text=name)).to_be_visible(timeout=15000)
    expect(page.get_by_text("Widget", exact=True)).to_have_count(0, timeout=15000)
