import os

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models import Item, User

MOCK_ITEMS = [
    {"sku": "WDG-001", "name": "Widget", "quantity": 50, "location": "A-01", "min_stock": 10},
    {"sku": "BOLT-M8", "name": "M8 Bolt", "quantity": 200, "location": "B-01", "min_stock": 50},
    {"sku": "BOX-S", "name": "Small Box", "quantity": 3, "location": "C-01", "min_stock": 10},
]


def _demo_users() -> list[User]:
    credential_names = (
        "DEMO_ADMIN_USERNAME",
        "DEMO_ADMIN_PASSWORD",
        "DEMO_CLERK_USERNAME",
        "DEMO_CLERK_PASSWORD",
    )
    credentials = {name: os.getenv(name, "").strip() for name in credential_names}
    missing = [name for name, value in credentials.items() if not value]
    if missing:
        raise RuntimeError(
            "Demo mode requires these environment variables: " + ", ".join(missing)
        )

    usernames = (
        credentials["DEMO_ADMIN_USERNAME"],
        credentials["DEMO_CLERK_USERNAME"],
    )
    passwords = (
        credentials["DEMO_ADMIN_PASSWORD"],
        credentials["DEMO_CLERK_PASSWORD"],
    )
    if usernames[0].casefold() == usernames[1].casefold():
        raise RuntimeError("Demo account usernames must be unique")
    if passwords[0] == passwords[1]:
        raise RuntimeError("Demo account passwords must be unique")
    if any(len(password) < 16 for password in passwords):
        raise RuntimeError("Demo account passwords must be at least 16 characters long")

    return [
        User(username=usernames[0], hashed_password=hash_password(passwords[0])),
        User(username=usernames[1], hashed_password=hash_password(passwords[1])),
    ]


def seed_db(db: Session) -> None:
    mode = os.getenv("APP_MODE", "production").strip().casefold()
    if mode == "production":
        return
    if mode not in {"development", "demo"}:
        raise RuntimeError("APP_MODE must be production, development, or demo")

    users = _demo_users()
    db.add_all(users)
    db.flush()
    db.add_all(Item(**item, created_by_id=users[0].id) for item in MOCK_ITEMS)
    db.commit()
