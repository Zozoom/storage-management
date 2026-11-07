from conftest import BASE, USER, PASSWORD


def login(page):
    response = page.request.post(
        f"{BASE}/api/auth/login/json",
        data={"username": USER, "password": PASSWORD},
    )
    assert response.status == 200, response.text()
    token = response.json()["access_token"]
    page.goto(BASE)
    page.evaluate("token => localStorage.setItem('storage_token', token)", token)
    page.goto(f"{BASE}/dashboard")
