from conftest import BASE, USER, PASSWORD
import time

from playwright.sync_api import expect


def login(page):
    page.goto(BASE)
    page.get_by_label("Username").fill(USER)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("heading", name="Inventory")).to_be_visible(timeout=15000)


def unique_value(label):
    return f"CYDIVO-QA-{label}-{int(time.time() * 1000)}"


def add_item(page, name, sku, quantity):
    page.get_by_role("button", name="+ Add item").click()
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Quantity").fill(str(quantity))
    page.get_by_role("button", name="Save item").click()
    row = page.get_by_role("row").filter(has_text=sku)
    expect(row).to_be_visible(timeout=15000)
    return row
