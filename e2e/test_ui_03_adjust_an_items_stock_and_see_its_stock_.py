from conftest import BASE, USER, PASSWORD
import time

from playwright.sync_api import expect

from ui_helpers import login


def test_adjust_item_stock_and_see_status_update(page):
    """Adjust an item’s stock and see its stock status update."""
    login(page)
    expect(page.get_by_role("heading", name="Inventory"), "Inventory dashboard should open").to_be_visible(timeout=15000)

    suffix = str(int(time.time() * 1000))
    name = f"CYDIVO-QA-{suffix} Stock Item"
    sku = f"CYDIVO-QA-{suffix}"

    page.get_by_role("button", name="+ Add item").click()
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Description (optional)").fill(f"CYDIVO-QA description {suffix}")
    page.get_by_label("Quantity").fill("2")
    page.get_by_label("Location").fill(f"QA-{suffix}")
    page.get_by_label("Restock below").fill("3")
    page.get_by_role("button", name="Save item").click()

    row = page.locator("tr").filter(has_text=sku)
    expect(row, "Created stock item should appear").to_be_visible(timeout=15000)
    quantity = row.locator("td").nth(2)
    expect(quantity, "Initial quantity should be two").to_contain_text("2", timeout=15000)
    expect(row.get_by_text("Low stock", exact=True), "Item should initially show low stock").to_be_visible(timeout=15000)

    page.get_by_role("button", name=f"Increase {name}").click()
    expect(quantity, "Quantity should increase by one").to_contain_text("3", timeout=15000)
    expect(row.get_by_text("In stock", exact=True), "Item should show in stock at the threshold").to_be_visible(timeout=15000)

    page.get_by_role("button", name=f"Decrease {name}").click()
    expect(quantity, "Quantity should decrease by one").to_contain_text("2", timeout=15000)
    expect(row.get_by_text("Low stock", exact=True), "Item should show low stock below the threshold").to_be_visible(timeout=15000)
