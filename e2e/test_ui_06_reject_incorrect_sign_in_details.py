from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect


def test_reject_incorrect_sign_in_details(page):
    """Reject incorrect sign-in details."""
    page.goto(f"{BASE.rstrip('/')}/")
    page.get_by_label("Username").fill(USER)
    page.get_by_label("Password").fill("definitely-not-the-correct-password")
    page.get_by_role("button", name="Sign in").click()

    expect(page.get_by_text("Invalid username or password", exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=15000)
    expect(page.get_by_role("heading", name="Inventory")).not_to_be_visible(timeout=15000)
    expect(page).to_have_url(f"{BASE.rstrip('/')}/", timeout=15000)
