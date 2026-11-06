from conftest import BASE, USER, PASSWORD
import re

from playwright.sync_api import expect


def login(page):
    page.goto(BASE)
    page.get_by_label("Username").fill(USER)
    page.get_by_label("Password").fill(PASSWORD)
    page.get_by_role("button", name="Sign in").click()
    expect(page).to_have_url(re.compile(r".*/dashboard/?$"), timeout=15000)


def unique_value(prefix):
    import time

    return f"CYDIVO-QA-{prefix}-{int(time.time() * 1000)}"
