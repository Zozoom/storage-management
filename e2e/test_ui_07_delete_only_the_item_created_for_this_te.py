from conftest import BASE, USER, PASSWORD
from playwright.sync_api import expect

from ui_helpers_2 import add_item, login, unique_value


def test_delete_only_the_item_created_for_this_test(page):
    """Delete only the item created for this test."""
    login(page)
    name = unique_value("Delete")
    sku = unique_value("SKU-Delete")
    row = add_item(page, name, sku, 1)

    page.once("dialog", lambda dialog: dialog.accept())
    row.get_by_role("button", name=f"Delete {name}").click()

    expect(row, "The test-created item should disappear after deletion").to_have_count(0, timeout=15000)
