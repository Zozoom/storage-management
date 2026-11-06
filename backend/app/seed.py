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
    if os.getenv("ENABLE_DEMO_DATA") != "1":
        return

    users = [User(username=u["username"], hashed_password=hash_password(u["password"])) for u in MOCK_USERS]
    db.add_all(users)
    db.flush()
    db.add_all(Item(**item, created_by_id=users[0].id) for item in MOCK_ITEMS)
    db.commit()
