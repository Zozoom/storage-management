from conftest import BASE, USER, PASSWORD

import uuid

from playwright.sync_api import expect


def login(page):
    page.goto(f"{BASE.rstrip('/')}/")
    page.get_by_label("Username").fill(USER)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("heading", name="Inventory")).to_be_visible(timeout=15000)
    expect(page).to_have_url(f"{BASE.rstrip('/')}/dashboard", timeout=15000)


def unique_value(prefix):
    return f"{prefix}-{uuid.uuid4().hex}"


def create_item(page, name, sku, location, quantity, min_stock):
    page.get_by_role("button", name="+ Add item").click()
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Quantity").fill(str(quantity))
    page.get_by_label("Location").fill(location)
    page.get_by_label("Restock below").fill(str(min_stock))
    page.get_by_role("button", name="Save item").click()
    expect(page.get_by_text(name, exact=True)).to_be_visible(timeout=15000)
