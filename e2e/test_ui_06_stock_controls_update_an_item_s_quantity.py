from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import add_item, login, unique_value


def test_stock_controls_update_quantity_and_stock_status(page):
    """Stock controls update an item's quantity and stock status."""
    login(page)
    suffix = unique_value()
    name = f"QA Stock Item {suffix}"
    add_item(
        page,
        name,
        f"QA-UI-{suffix}",
        quantity=1,
        location=f"QA-SHELF-{suffix}",
        min_stock=2,
    )
    row = page.get_by_role("row").filter(has_text=name)
    quantity_cell = row.get_by_role("cell").nth(2)
    status_cell = row.get_by_role("cell").nth(3)

    expect(quantity_cell).to_contain_text("1", timeout=15000)
    expect(status_cell).to_contain_text("Low stock", timeout=15000)
    row.get_by_role("button", name=f"Increase {name}").click()
    expect(quantity_cell).to_contain_text("2", timeout=15000)
    expect(status_cell).to_contain_text("In stock", timeout=15000)
    row.get_by_role("button", name=f"Decrease {name}").click()
    expect(quantity_cell).to_contain_text("1", timeout=15000)
    expect(status_cell).to_contain_text("Low stock", timeout=15000)
