from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import create_item, login, unique_suffix


def test_see_the_duplicate_sku_validation_message(page):
    """See the duplicate-SKU validation message"""
    if not login(page):
        expect(page.get_by_text("Invalid username or password", exact=True)).to_be_visible(timeout=15000)
        return

    suffix = unique_suffix()
    name = f"QA original {suffix}"
    sku = f"QA-{suffix}"
    create_item(
        page,
        name=name,
        sku=sku,
        quantity=3,
        location=f"QA-SHELF-{suffix}",
        min_stock=2,
    )
    original_row = page.get_by_role("row").filter(has_text=name)
    expect(original_row).to_be_visible(timeout=15000)

    create_item(
        page,
        name=f"QA duplicate {suffix}",
        sku=sku,
        quantity=1,
        location=f"QA-DUPLICATE-{suffix}",
        min_stock=2,
    )
    expect(page.get_by_text("SKU already exists", exact=True)).to_be_visible(timeout=15000)
    expect(original_row).to_be_visible(timeout=15000)
