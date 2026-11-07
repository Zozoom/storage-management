from conftest import BASE, USER, PASSWORD
import time

from playwright.sync_api import expect
from ui_helpers_2 import login


def test_filter_inventory_by_a_unique_location(page):
    """Filter inventory by a unique location."""
    login(page)
    suffix = str(int(time.time() * 1000))
    name = f"CYDIVO-QA-Location-{suffix}"
    sku = f"CYDIVO-QA-SKU-{suffix}"
    location = f"CYDIVO-QA-Bin-{suffix}"

    page.get_by_role("button", name="+ Add item").click()
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Location").fill(location)
    page.get_by_role("button", name="Save item").click()

    row = page.locator("tbody tr").filter(has_text=name)
    expect(row, "The newly created item should appear in inventory").to_be_visible(timeout=15000)
    page.get_by_placeholder("Search by name, SKU or location…").fill(location)
    expect(row, "The unique location should match the new item").to_be_visible(timeout=15000)
    rows = page.locator("tbody tr")
    expect(rows, "Only the item matching the unique location should be shown").to_have_count(1, timeout=15000)
