from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect


def test_incorrect_sign_in_details_are_rejected(page):
    """Incorrect sign-in details are rejected."""
    page.goto(BASE.rstrip("/") + "/")
    page.locator("#username").fill(f"CYDIVO-QA-UNKNOWN-{int(__import__('time').time() * 1000)}")
    page.locator("#password").fill("CYDIVO-QA-INVALID-PASSWORD")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Invalid username or password", exact=True), "Invalid credentials should show an error").to_be_visible(timeout=15000)
    assert page.url == BASE.rstrip("/") + "/", "Rejected credentials should keep the user on the sign-in page"
