import os

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models import Item, User

MOCK_USERS = [
    {"username": "admin", "password": "admin123"},
    {"username": "clerk", "password": "clerk123"},
]

MOCK_ITEMS = [
    {"sku": "WDG-001", "name": "Widget", "quantity": 50, "location": "A-01", "min_stock": 10},
    {"sku": "BOLT-M8", "name": "M8 Bolt", "quantity": 200, "location": "B-01", "min_stock": 50},
    {"sku": "BOX-S", "name": "Small Box", "quantity": 3, "location": "C-01", "min_stock": 10},
]


def _users_to_seed() -> list[dict[str, str]]:
    is_production = any(
        os.getenv(name, "").strip().lower() == "production"
        for name in ("APP_ENV", "ENVIRONMENT", "VERCEL_ENV")
    )
    if not is_production:
        return MOCK_USERS

    username = os.getenv("INITIAL_ADMIN_USERNAME", "").strip()
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "")
    if not username or len(password) < 12:
        raise RuntimeError(
            "Production seeding requires INITIAL_ADMIN_USERNAME and an "
            "INITIAL_ADMIN_PASSWORD of at least 12 characters"
        )
    return [{"username": username, "password": password}]


def seed_db(db: Session) -> None:
    users = [
        User(username=user["username"], hashed_password=hash_password(user["password"]))
        for user in _users_to_seed()
    ]
    db.add_all(users)
    db.flush()
    db.add_all(Item(**item, created_by_id=users[0].id) for item in MOCK_ITEMS)
    db.commit()
