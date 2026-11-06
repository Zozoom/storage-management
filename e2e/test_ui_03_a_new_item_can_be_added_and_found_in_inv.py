from conftest import BASE, USER, PASSWORD

import time

from playwright.sync_api import expect

from ui_helpers import create_item, login


def test_new_item_can_be_added_and_found_in_inventory(page):
    """A new item can be added and found in inventory."""
    login(page)
    unique = f"CYDIVO-QA-{int(time.time() * 1000)}"
    name = f"{unique}-Item"
    sku = f"{unique}-SKU"
    location = f"{unique}-Location"
    description = f"{unique}-Description"
    create_item(
        page,
        {
            "name": name,
            "sku": sku,
            "description": description,
            "quantity": 7,
            "location": location,
            "min_stock": 2,
        },
    )
    page.reload()
    expect(page.get_by_text(name, exact=True), "The new item should appear in the inventory").to_be_visible(timeout=15000)
    expect(page.get_by_text(sku, exact=True), "The new item's SKU should be displayed").to_be_visible(timeout=15000)
    expect(page.get_by_text(location, exact=True), "The new item's location should be displayed").to_be_visible(timeout=15000)
    expect(page.get_by_text(description, exact=True), "The new item's description should be displayed").to_be_visible(timeout=15000)
