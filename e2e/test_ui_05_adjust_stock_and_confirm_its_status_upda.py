from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_value


def test_adjust_stock_and_confirm_its_status_updates(page):
    """Adjust stock and confirm its status updates"""
    login(page)
    suffix = unique_value("Adjust")
    name = f"{suffix} Stock Item"
    sku = f"{suffix}-SKU"
    create_item(page, name=name, sku=sku, quantity=1, location=f"{suffix}-LOC", min_stock=2)

    row = page.get_by_role("row").filter(has_text=sku)
    expect(row, "The new item should initially be visible").to_be_visible(timeout=15000)
    expect(row.get_by_text("Low stock"), "Quantity 1 should be below the restock threshold").to_be_visible(timeout=15000)
    row.get_by_role("button", name=f"Increase {name}").click()

    expect(row.get_by_role("cell").nth(2), "The item quantity should update to 2").to_contain_text("2", timeout=15000)
    expect(row.get_by_role("cell").nth(3).get_by_text("In stock"), "The item should change to In stock at the threshold").to_be_visible(timeout=15000)
