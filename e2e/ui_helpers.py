from conftest import BASE, USER, PASSWORD

from playwright.sync_api import expect
import time


def login(page):
    page.goto(f"{BASE}/")
    expect(page.get_by_role("heading", name="Welcome back")).to_be_visible(timeout=15000)
    page.get_by_label("Username").fill(USER)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_function(
        "() => location.pathname === '/dashboard' || document.body.innerText.includes('Invalid username or password')",
        timeout=15000,
    )
    if page.locator("h1").filter(has_text="Inventory").is_visible():
        return True
    expect(page.get_by_text("Invalid username or password", exact=True)).to_be_visible(timeout=15000)
    return False


def unique_suffix():
    return f"CYDIVO-QA-{int(time.time() * 1000)}"


def create_item(page, *, name, sku, quantity, location, min_stock, description=""):
    page.get_by_role("button", name="+ Add item").click()
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Quantity").fill(str(quantity))
    page.get_by_label("Location").fill(location)
    page.get_by_label("Restock below").fill(str(min_stock))
    page.get_by_label("Description (optional)").fill(description)
    page.get_by_role("button", name="Save item").click()
