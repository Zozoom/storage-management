from conftest import BASE, USER, PASSWORD


def login(page):
    """Authenticate with the deployment administrator and open the dashboard."""
    root_url = BASE.rstrip("/") + "/"
    page.goto(root_url)
    response = page.request.post(
        BASE.rstrip("/") + "/api/auth/login/json",
        data={"username": USER, "password": PASSWORD},
    )
    assert response.ok, f"Administrator sign-in failed: {response.status} {response.text()}"
    token = response.json()["access_token"]
    page.evaluate("token => localStorage.setItem('storage_token', token)", token)
    page.goto(BASE.rstrip("/") + "/dashboard")
