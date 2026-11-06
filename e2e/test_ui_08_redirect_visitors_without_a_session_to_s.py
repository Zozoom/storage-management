from conftest import BASE, USER, PASSWORD
from playwright.sync_api import expect


def test_redirect_visitors_without_a_session_to_sign_in(page):
    """Redirect visitors without a session to sign in."""
    page.goto(BASE)
    page.evaluate("localStorage.removeItem('storage_token')")
    page.goto(BASE.rstrip("/") + "/dashboard")

    expect(page.get_by_role("heading", name="Welcome back"), "Visitors without a session should see the sign-in form").to_be_visible(timeout=15000)
    expect(page, "Visitors without a session should be redirected to the sign-in page").to_have_url(BASE.rstrip("/") + "/", timeout=15000)
