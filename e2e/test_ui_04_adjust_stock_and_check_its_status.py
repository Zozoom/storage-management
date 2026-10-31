from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_suffix


def test_adjust_stock_and_check_its_status(page):
    """Adjust stock and check its status"""
    if not login(page):
        expect(page.get_by_text("Invalid username or password", exact=True)).to_be_visible(timeout=15000)
        return

    suffix = unique_suffix()
    name = f"QA stock {suffix}"
    create_item(
        page,
        name=name,
        sku=f"QA-{suffix}",
        quantity=1,
        location=f"QA-SHELF-{suffix}",
        min_stock=2,
    )
    item_row = page.get_by_role("row").filter(has_text=name)
    expect(item_row).to_be_visible(timeout=15000)
    expect(item_row.get_by_text("1", exact=True)).to_be_visible(timeout=15000)
    expect(item_row.get_by_text("Low stock", exact=True)).to_be_visible(timeout=15000)

    page.get_by_role("button", name=f"Increase {name}").click()
    expect(item_row.get_by_text("2", exact=True)).to_be_visible(timeout=15000)
    expect(item_row.get_by_text("In stock", exact=True)).to_be_visible(timeout=15000)

    page.get_by_role("button", name=f"Decrease {name}").click()
    expect(item_row.get_by_text("1", exact=True)).to_be_visible(timeout=15000)
    expect(item_row.get_by_text("Low stock", exact=True)).to_be_visible(timeout=15000)
