from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_value


def test_adjust_item_stock_and_check_status(page):
    """Adjust an item's stock and check its status."""
    login(page)
    suffix = unique_value("CYDIVO-QA")
    name = f"Adjustable item {suffix}"
    sku = f"SKU-{suffix}"
    create_item(page, name, sku, f"LOC-{suffix}", quantity=1, min_stock=3)

    row = page.get_by_role("row").filter(has_text=sku)
    expect(row.get_by_text("1", exact=True)).to_be_visible(timeout=15000)
    expect(row.get_by_text("Low stock", exact=True)).to_be_visible(timeout=15000)

    page.get_by_role("button", name=f"Increase {name}").click()
    expect(row.get_by_text("2", exact=True)).to_be_visible(timeout=15000)
    expect(row.get_by_text("Low stock", exact=True)).to_be_visible(timeout=15000)

    page.get_by_role("button", name=f"Decrease {name}").click()
    expect(row.get_by_text("1", exact=True)).to_be_visible(timeout=15000)
    expect(row.get_by_text("Low stock", exact=True)).to_be_visible(timeout=15000)
    expect(row.get_by_text(name, exact=True)).to_be_visible(timeout=15000)
