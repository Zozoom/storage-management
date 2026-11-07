from conftest import BASE, USER, PASSWORD
import time

from playwright.sync_api import expect
from ui_helpers_2 import login


def test_delete_only_the_item_created_for_this_test(page):
    """Delete only the item created for this test."""
    login(page)
    rows = page.locator("tbody tr")
    existing_rows = rows.all_text_contents()
    suffix = str(int(time.time() * 1000))
    name = f"CYDIVO-QA-Delete-{suffix}"
    sku = f"CYDIVO-QA-SKU-{suffix}"

    page.get_by_role("button", name="+ Add item").click()
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_role("button", name="Save item").click()

    row = rows.filter(has_text=name)
    expect(row, "The test item should appear before deletion").to_be_visible(timeout=15000)
    page.once("dialog", lambda dialog: dialog.accept())
    row.get_by_role("button", name=f"Delete {name}").click()
    expect(row, "The test item should disappear after confirmation").to_have_count(0, timeout=15000)

    remaining_rows = rows.all_text_contents()
    assert all(text in remaining_rows for text in existing_rows), "Deleting the test item should leave previously listed items intact"
