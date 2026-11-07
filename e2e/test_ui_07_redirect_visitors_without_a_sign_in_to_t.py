from conftest import BASE, USER, PASSWORD
from playwright.sync_api import expect


def test_redirect_visitors_without_a_sign_in_to_the_login_page(page):
    """Redirect visitors without a sign-in to the login page."""
    root_url = BASE.rstrip("/") + "/"
    page.goto(BASE.rstrip("/") + "/dashboard")

    page.wait_for_url(root_url, timeout=15000)
    expect(
        page.get_by_role("heading", name="Inventory"),
        "Inventory should not be visible to a visitor without a sign-in",
    ).not_to_be_visible(timeout=15000)
