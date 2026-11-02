from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import add_item, login, unique_value


def test_newly_created_item_appears_in_inventory(page):
    """A newly created item appears in the inventory."""
    login(page)
    suffix = unique_value()
    name = f"QA UI Item {suffix}"
    sku = f"QA-UI-{suffix}"
    description = f"Description {suffix}"
    location = f"QA-SHELF-{suffix}"

    add_item(page, name, sku, quantity=7, location=location, min_stock=3, description=description)

    row = page.get_by_role("row").filter(has_text=name)
    expect(row).to_be_visible(timeout=15000)
    expect(row).to_contain_text(sku, timeout=15000)
    expect(row).to_contain_text(description, timeout=15000)
    expect(row).to_contain_text(location, timeout=15000)
    expect(row).to_contain_text("7", timeout=15000)
    expect(row).to_contain_text("In stock", timeout=15000)
