from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_value


def test_delete_only_item_created_for_check(page):
    """Delete only the item created for this check."""
    login(page)
    suffix = unique_value("CYDIVO-QA")
    name = f"Deletable item {suffix}"
    sku = f"SKU-{suffix}"
    create_item(page, name, sku, f"LOC-{suffix}", quantity=4, min_stock=1)

    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name=f"Delete {name}").click()

    expect(page.get_by_text(name, exact=True)).not_to_be_visible(timeout=15000)
    expect(page.get_by_text(sku, exact=True)).not_to_be_visible(timeout=15000)
    expect(page.get_by_text("WDG-001", exact=True)).to_be_visible(timeout=15000)
