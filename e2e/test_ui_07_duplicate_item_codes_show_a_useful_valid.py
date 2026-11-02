from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import add_item, login, unique_value


def test_duplicate_item_codes_show_validation_error(page):
    """Duplicate item codes show a useful validation error."""
    login(page)
    suffix = unique_value()
    original_name = f"QA Original Item {suffix}"
    duplicate_name = f"QA Duplicate Item {suffix}"
    sku = f"QA-UI-{suffix}"
    add_item(page, original_name, sku, location=f"QA-SHELF-{suffix}")

    page.get_by_role("button", name="+ Add item").click()
    page.get_by_label("Name").fill(duplicate_name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Quantity").fill("4")
    page.get_by_label("Location").fill(f"QA-OTHER-{suffix}")
    page.get_by_label("Restock below").fill("2")
    page.get_by_label("Description (optional)").fill(f"Duplicate attempt {suffix}")
    page.get_by_role("button", name="Save item").click()

    expect(page.get_by_text("SKU already exists", exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_role("row").filter(has_text=original_name)).to_be_visible(timeout=15000)
    expect(page.get_by_role("row").filter(has_text=duplicate_name)).to_have_count(0, timeout=15000)
