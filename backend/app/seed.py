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
    users: dict[str, User] = {}
    is_development = os.getenv("APP_ENV") == "development"
    if is_development:
        usernames = [user["username"] for user in MOCK_USERS]
        users = {
            user.username: user
            for user in db.query(User).filter(User.username.in_(usernames)).all()
        }
        for user_data in MOCK_USERS:
            if user_data["username"] not in users:
                user = User(
                    username=user_data["username"],
                    hashed_password=hash_password(user_data["password"]),
                )
                db.add(user)
                users[user.username] = user
        db.flush()

    skus = [item["sku"] for item in MOCK_ITEMS]
    existing_skus = {
        item.sku for item in db.query(Item).filter(Item.sku.in_(skus)).all()
    }
    creator_id = users["admin"].id if is_development else None
    for item_data in MOCK_ITEMS:
        if item_data["sku"] not in existing_skus:
            db.add(Item(**item_data, created_by_id=creator_id))
    db.commit()
