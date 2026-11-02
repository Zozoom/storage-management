from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect


def test_dashboard_redirects_visitors_who_are_not_signed_in(page):
    """The dashboard redirects visitors who are not signed in."""
    page.goto(f"{BASE.rstrip('/')}/dashboard")

    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=15000)
    expect(page.get_by_role("heading", name="Inventory")).to_have_count(0, timeout=15000)
