from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_suffix


def test_delete_only_an_item_created_for_this_test(page):
    """Delete only an item created for this test"""
    if not login(page):
        expect(page.get_by_text("Invalid username or password", exact=True)).to_be_visible(timeout=15000)
        return

    suffix = unique_suffix()
    name = f"QA delete {suffix}"
    sku = f"QA-{suffix}"
    create_item(
        page,
        name=name,
        sku=sku,
        quantity=2,
        location=f"QA-SHELF-{suffix}",
        min_stock=1,
    )
    item_row = page.get_by_role("row").filter(has_text=name)
    expect(item_row).to_be_visible(timeout=15000)

    dialogs = []

    def accept_delete_dialog(dialog):
        dialogs.append(dialog.message)
        dialog.accept()

    page.once("dialog", accept_delete_dialog)
    page.get_by_role("button", name=f"Delete {name}").click()
    assert dialogs == ["Delete this item?"], f"Expected the item deletion confirmation, got {dialogs}"

    search = page.get_by_role("searchbox", name="Search items")
    search.fill(sku)
    expect(page.get_by_text("No items found.", exact=True)).to_be_visible(timeout=15000)
