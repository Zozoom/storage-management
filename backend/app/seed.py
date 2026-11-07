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


def seed_db(db: Session) -> None:
    if os.getenv("TESTING") == "1":
        user_credentials = MOCK_USERS
    else:
        username = os.getenv("INITIAL_ADMIN_USERNAME")
        password = os.getenv("INITIAL_ADMIN_PASSWORD")
        if bool(username) != bool(password):
            raise RuntimeError(
                "INITIAL_ADMIN_USERNAME and INITIAL_ADMIN_PASSWORD must be set together"
            )
        user_credentials = (
            [{"username": username, "password": password}] if username and password else []
        )

    users = [
        User(username=u["username"], hashed_password=hash_password(u["password"]))
        for u in user_credentials
    ]
    db.add_all(users)
    db.flush()
    created_by_id = users[0].id if users else None
    db.add_all(Item(**item, created_by_id=created_by_id) for item in MOCK_ITEMS)
    db.commit()
