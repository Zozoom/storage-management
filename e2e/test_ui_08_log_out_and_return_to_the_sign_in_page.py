from conftest import BASE, USER, PASSWORD
from playwright.sync_api import expect
from ui_helpers_3 import login


def test_log_out_and_return_to_the_sign_in_page(page):
    """Log out and return to the sign-in page."""
    root_url = BASE.rstrip("/") + "/"
    login(page)

    expect(
        page.get_by_role("heading", name="Inventory"),
        "The signed-in administrator should see Inventory",
    ).to_be_visible(timeout=15000)
    page.get_by_role("button", name="Log out").click()
    page.wait_for_url(root_url, timeout=15000)

    page.goto(BASE.rstrip("/") + "/dashboard")
    page.wait_for_url(root_url, timeout=15000)
    expect(
        page.get_by_role("heading", name="Inventory"),
        "Inventory should not be visible after logout",
    ).not_to_be_visible(timeout=15000)
