from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import login


def test_find_seeded_stock_on_the_dashboard(page):
    """Find seeded stock on the dashboard"""
    if not login(page):
        expect(page.get_by_text("Invalid username or password", exact=True)).to_be_visible(timeout=15000)
        return

    expect(page.get_by_role("heading", name="Inventory")).to_be_visible(timeout=15000)
    search = page.get_by_role("searchbox", name="Search items")
    expect(search).to_be_visible(timeout=15000)

    widget = page.get_by_role("row").filter(has_text="Widget")
    bolt = page.get_by_role("row").filter(has_text="M8 Bolt")
    small_box = page.get_by_role("row").filter(has_text="Small Box")
    expect(widget).to_be_visible(timeout=15000)
    expect(bolt).to_be_visible(timeout=15000)
    expect(small_box).to_be_visible(timeout=15000)
    expect(small_box.get_by_text("Low stock", exact=True)).to_be_visible(timeout=15000)

    search.fill("BOX-S")
    expect(small_box).to_be_visible(timeout=15000)
    expect(widget).not_to_be_visible(timeout=15000)

    search.fill("A-01")
    expect(widget).to_be_visible(timeout=15000)
    expect(page.get_by_role("row").filter(has_text="WDG-001")).to_be_visible(timeout=15000)

    search.fill("")
    expect(widget).to_be_visible(timeout=15000)
    expect(bolt).to_be_visible(timeout=15000)
    expect(small_box).to_be_visible(timeout=15000)
