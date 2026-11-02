from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect


def test_incorrect_password_is_rejected_at_sign_in(page):
    """An incorrect password is rejected at sign-in."""
    page.goto(BASE)
    page.get_by_label("Username").fill(USER)
    page.get_by_label("Password").fill(f"incorrect-{PASSWORD}")
    page.get_by_role("button", name="Sign in").click()

    expect(page.get_by_text("Invalid username or password", exact=True)).to_be_visible(timeout=15000)
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=15000)
    expect(page.get_by_role("heading", name="Inventory")).to_have_count(0, timeout=15000)
