from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect

from ui_helpers import unique_value


def test_reject_incorrect_sign_in_details(page):
    """Reject incorrect sign-in details."""
    page.goto(BASE.rstrip("/") + "/")
    expect(page.get_by_label("Username"), "The sign-in form should be visible").to_be_visible(timeout=15000)
    page.get_by_label("Username").fill(unique_value())
    page.get_by_label("Password").fill("arbitrary-password")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Invalid username or password", exact=True), "Invalid credentials should be reported").to_be_visible(timeout=15000)
    # The failed attempt starts a cooldown; allow its initial delay to expire before later sign-ins.
    page.wait_for_timeout(1200)
