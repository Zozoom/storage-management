from conftest import BASE, USER, PASSWORD
import time

from playwright.sync_api import expect


def unique_value(label: str) -> str:
    return f"CYDIVO-QA-{label}-{int(time.time() * 1000)}"


def login(page) -> None:
    page.goto(f"{BASE.rstrip('/')}/")
    page.get_by_label("Username").fill(USER)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("heading", name="Inventory")).to_be_visible(timeout=15000)


def create_item(page, *, name: str, sku: str, quantity: int, location: str, min_stock: int, description: str = "") -> None:
    page.get_by_role("button", name="+ Add item").click()
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Description (optional)").fill(description)
    page.get_by_label("Quantity").fill(str(quantity))
    page.get_by_label("Location").fill(location)
    page.get_by_label("Restock below").fill(str(min_stock))
    page.get_by_role("button", name="Save item").click()
