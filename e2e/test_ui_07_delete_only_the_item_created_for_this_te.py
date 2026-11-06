from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_value


def test_delete_only_the_item_created_for_this_test(page):
    """Delete only the item created for this test"""
    login(page)
    suffix = unique_value("Delete")
    name = f"{suffix} Delete Item"
    sku = f"{suffix}-SKU"
    create_item(page, name=name, sku=sku, quantity=4, location=f"{suffix}-LOC", min_stock=2)

    row = page.get_by_role("row").filter(has_text=sku)
    expect(row, "The item created for deletion should be visible").to_be_visible(timeout=15000)
    page.once("dialog", lambda dialog: dialog.accept())
    row.get_by_role("button", name=f"Delete {name}").click()
    expect(row, "The selected item should disappear after confirming deletion").to_have_count(0, timeout=15000)
