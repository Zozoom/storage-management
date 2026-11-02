from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import add_item, login, unique_value


def test_item_can_be_deleted_without_removing_other_inventory(page):
    """An item can be deleted without removing other inventory."""
    login(page)
    suffix = unique_value()
    name = f"QA Delete Item {suffix}"
    add_item(page, name, f"QA-UI-{suffix}", location=f"QA-SHELF-{suffix}")
    row = page.get_by_role("row").filter(has_text=name)
    expect(row).to_be_visible(timeout=15000)

    page.once("dialog", lambda dialog: dialog.accept())
    row.get_by_role("button", name=f"Delete {name}").click()

    expect(row).to_have_count(0, timeout=15000)
    expect(page.get_by_text("Widget", exact=True)).to_be_visible(timeout=15000)
