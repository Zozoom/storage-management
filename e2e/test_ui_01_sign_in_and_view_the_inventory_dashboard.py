from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login


def test_sign_in_and_view_inventory_dashboard(page):
    """Sign in and view the inventory dashboard."""
    login(page)

    expect(page.get_by_text("See what you have, where it is, and what needs restocking.")).to_be_visible(timeout=15000)
    expect(page.get_by_text("Products", exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_text("Units in stock", exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_text("Need restocking", exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_text("Widget", exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_text("WDG-001", exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_label("Search items")).to_be_visible(timeout=15000)
    expect(page.get_by_role("button", name="+ Add item")).to_be_visible(timeout=15000)
    expect(page.get_by_role("button", name="Log out")).to_be_visible(timeout=15000)
