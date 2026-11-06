from conftest import BASE, USER, PASSWORD

import time
from playwright.sync_api import expect


def unique_value():
    return f"CYDIVO-QA-{time.time_ns()}"


def login(page):
    page.goto(BASE.rstrip("/") + "/")
    expect(page.get_by_label("Username"), "The sign-in form should be visible").to_be_visible(timeout=15000)
    page.get_by_label("Username").fill(USER)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("heading", name="Inventory"), "The signed-in dashboard should open").to_be_visible(timeout=15000)


def add_item(page, name, sku, quantity="8", location="A-01", min_stock="5", description=""):
    page.get_by_role("button", name="+ Add item").click()
    expect(page.get_by_role("heading", name="New item"), "The new-item form should open").to_be_visible(timeout=15000)
    page.get_by_label("Name").fill(name)
    page.get_by_label("SKU").fill(sku)
    page.get_by_label("Quantity").fill(quantity)
    page.get_by_label("Location").fill(location)
    page.get_by_label("Restock below").fill(min_stock)
    if description:
        page.get_by_label("Description (optional)").fill(description)
    page.get_by_role("button", name="Save item").click()
