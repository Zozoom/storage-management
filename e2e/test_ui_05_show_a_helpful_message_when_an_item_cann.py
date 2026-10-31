from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login, unique_value


def test_duplicate_sku_shows_helpful_creation_error(page):
    """Show a helpful message when an item cannot be created."""
    login(page)
    name = f"Duplicate attempt {unique_value('CYDIVO-QA')}"
    page.get_by_role("button", name="+ Add item").click()
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill("WDG-001")
    page.get_by_label("Quantity").fill("5")
    page.get_by_label("Location").fill("QA-LOCATION")
    page.get_by_label("Restock below").fill("2")
    page.get_by_role("button", name="Save item").click()

    expect(page.get_by_text("SKU already exists", exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_text(name, exact=True)).not_to_be_visible(timeout=15000)
    expect(page.get_by_text("WDG-001", exact=True)).to_be_visible(timeout=15000)
