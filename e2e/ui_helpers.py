from conftest import BASE, USER, PASSWORD

import time
from playwright.sync_api import expect


def unique_value():
    return f"CYDIVO-QA-{time.time_ns()}"


def login(page):
    page.goto(BASE)
    page.get_by_label("Username").fill(USER)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("heading", name="Inventory")).to_be_visible(timeout=15000)


def add_item(page, name, sku, quantity=4, location="QA-SHELF", min_stock=2, description="QA test item"):
    page.get_by_role("button", name="+ Add item").click()
    expect(page.get_by_role("heading", name="New item")).to_be_visible(timeout=15000)
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Quantity").fill(str(quantity))
    page.get_by_label("Location").fill(location)
    page.get_by_label("Restock below").fill(str(min_stock))
    page.get_by_label("Description (optional)").fill(description)
    page.get_by_role("button", name="Save item").click()
    expect(page.get_by_role("heading", name="New item")).to_be_hidden(timeout=15000)
