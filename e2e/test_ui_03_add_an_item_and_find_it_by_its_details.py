from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_suffix


def test_add_an_item_and_find_it_by_its_details(page):
    """Add an item and find it by its details"""
    if not login(page):
        expect(page.get_by_text("Invalid username or password", exact=True)).to_be_visible(timeout=15000)
        return

    suffix = unique_suffix()
    name = f"QA item {suffix}"
    sku = f"QA-{suffix}"
    location = f"QA-SHELF-{suffix}"
    create_item(
        page,
        name=name,
        sku=sku,
        quantity=4,
        location=location,
        min_stock=5,
        description=f"Created by test run {suffix}",
    )

    item_row = page.get_by_role("row").filter(has_text=name)
    expect(item_row).to_be_visible(timeout=15000)
    expect(item_row.get_by_text("Low stock", exact=True)).to_be_visible(timeout=15000)

    search = page.get_by_role("searchbox", name="Search items")
    search.fill(sku)
    expect(item_row).to_be_visible(timeout=15000)
    search.fill(location)
    expect(item_row).to_be_visible(timeout=15000)
    search.fill("")
    expect(item_row).to_be_visible(timeout=15000)
