from conftest import BASE, USER, PASSWORD
from ui_helpers_2 import login

from playwright.sync_api import expect
import re


def test_logging_out_prevents_access_to_inventory_without_signing_in_again(page):
    """Logging out prevents access to the inventory without signing in again."""
    login(page)
    page.get_by_role("button", name="Log out").click()
    expect(page).to_have_url(re.compile(r".*/$"), timeout=15000)
    expect(page.get_by_role("heading", name="Welcome back"), "Logging out should return to the sign-in page").to_be_visible(timeout=15000)

    page.goto(f"{BASE.rstrip('/')}/dashboard")
    expect(page).to_have_url(re.compile(r".*/$"), timeout=15000)
    expect(page.get_by_role("heading", name="Welcome back"), "The dashboard should require signing in again after logout").to_be_visible(timeout=15000)
