from conftest import BASE, USER, PASSWORD

import time

from playwright.sync_api import expect

from ui_helpers import create_item, login


def test_changing_stock_updates_quantity_and_status(page):
    """Changing stock updates the quantity and stock status."""
    login(page)
    unique = f"CYDIVO-QA-{int(time.time() * 1000)}"
    name = f"{unique}-Item"
    create_item(
        page,
        {
            "name": name,
            "sku": f"{unique}-SKU",
            "quantity": 2,
            "location": f"{unique}-Location",
            "min_stock": 2,
        },
    )
    page.reload()
    row = page.get_by_role("row").filter(has_text=name)
    expect(row, "The newly created item should appear in the inventory").to_be_visible(timeout=15000)
    row.get_by_role("button", name=f"Decrease {name}").click()
    expect(row.get_by_text("1", exact=True), "The item quantity should decrease to one").to_be_visible(timeout=15000)
    expect(row.get_by_text("Low stock", exact=True), "The item should be marked low stock").to_be_visible(timeout=15000)
