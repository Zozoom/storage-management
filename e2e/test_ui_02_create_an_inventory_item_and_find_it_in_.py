from conftest import BASE, USER, PASSWORD
import time

from playwright.sync_api import expect

from ui_helpers import login


def test_create_inventory_item_and_find_it_in_the_list(page):
    """Create an inventory item and find it in the list."""
    login(page)
    expect(page.get_by_role("heading", name="Inventory"), "Inventory dashboard should open").to_be_visible(timeout=15000)

    suffix = str(int(time.time() * 1000))
    name = f"CYDIVO-QA-{suffix} Item"
    sku = f"CYDIVO-QA-{suffix}"
    description = f"CYDIVO-QA description {suffix}"
    location = f"QA-{suffix}"

    page.get_by_role("button", name="+ Add item").click()
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Description (optional)").fill(description)
    page.get_by_label("Quantity").fill("7")
    page.get_by_label("Location").fill(location)
    page.get_by_label("Restock below").fill("2")
    page.get_by_role("button", name="Save item").click()

    row = page.locator("tr").filter(has_text=sku)
    expect(row, "Created item should appear in the inventory").to_be_visible(timeout=15000)
    expect(row, "Created item should show its name").to_contain_text(name, timeout=15000)
    expect(row, "Created item should show its description").to_contain_text(description, timeout=15000)
    expect(row, "Created item should show its location").to_contain_text(location, timeout=15000)
    assert row.locator("td").nth(2).inner_text().strip() == "7", "Created item should have the entered quantity"

    page.get_by_label("Search items").fill(sku)
    expect(row, "Searching by SKU should show the created item").to_be_visible(timeout=15000)
