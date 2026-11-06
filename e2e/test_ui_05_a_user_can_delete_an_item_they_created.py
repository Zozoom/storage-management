from conftest import BASE, USER, PASSWORD
from ui_helpers_2 import login, unique_value

from playwright.sync_api import expect


def test_user_can_delete_an_item_they_created(page):
    """A user can delete an item they created."""
    login(page)
    name = unique_value("DELETE-NAME")
    sku = unique_value("DELETE-SKU")

    page.get_by_role("button", name="Add item").click()
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_role("button", name="Save item").click()

    row = page.get_by_role("row").filter(has_text=name)
    expect(row, "The newly created item should appear in inventory").to_be_visible(timeout=15000)

    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name=f"Delete {name}").click()

    expect(page.get_by_text(name, exact=True), "The deleted item should no longer be found by its unique name").to_have_count(0, timeout=15000)
