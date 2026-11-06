from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect


def test_redirect_visitors_without_a_session_to_sign_in(page):
    """Redirect visitors without a session to sign in"""
    page.goto(f"{BASE.rstrip('/')}/dashboard")
    expect(page.get_by_role("heading", name="Welcome back"), "A visitor without a saved session should be redirected to sign in").to_be_visible(timeout=15000)
    expect(page.get_by_role("heading", name="Inventory"), "Inventory should not be visible without a session").to_have_count(0, timeout=15000)
