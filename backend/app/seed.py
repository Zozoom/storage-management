from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models import Item, User

MOCK_USERS = [
    {"username": "admin", "password": "admin123"},
    {"username": "clerk", "password": "clerk123"},
]

MOCK_ITEMS = [
    {
        "sku": "WDG-001",
        "name": "Widget Alpha",
        "description": "Standard widget for assembly line A",
        "quantity": 120,
        "location": "A-01",
        "min_stock": 20,
    },
    {
        "sku": "WDG-002",
        "name": "Widget Beta",
        "description": "Heavy-duty widget",
        "quantity": 8,
        "location": "A-02",
        "min_stock": 15,
    },
    {
        "sku": "BOLT-M8",
        "name": "M8 Hex Bolt",
        "description": "Pack of 100",
        "quantity": 450,
        "location": "B-12",
        "min_stock": 100,
    },
    {
        "sku": "NUT-M8",
        "name": "M8 Hex Nut",
        "description": "Pack of 100",
        "quantity": 12,
        "location": "B-13",
        "min_stock": 50,
    },
    {
        "sku": "CBL-USB",
        "name": "USB-C Cable 2m",
        "description": "Braided charging cable",
        "quantity": 64,
        "location": "C-04",
        "min_stock": 25,
    },
    {
        "sku": "BOX-S",
        "name": "Shipping Box S",
        "description": "Small corrugated box",
        "quantity": 3,
        "location": "D-01",
        "min_stock": 30,
    },
    {
        "sku": "TAPE-CLR",
        "name": "Clear Packing Tape",
        "description": "48mm x 66m roll",
        "quantity": 88,
        "location": "D-08",
        "min_stock": 20,
    },
    {
        "sku": "LBL-A4",
        "name": "A4 Shipping Labels",
        "description": "Sheet of 10 labels",
        "quantity": 200,
        "location": "E-02",
        "min_stock": 40,
    },
]


def seed_db(db: Session) -> None:
    if db.query(User).count() == 0:
        for u in MOCK_USERS:
            db.add(
                User(
                    username=u["username"],
                    hashed_password=hash_password(u["password"]),
                )
            )
        db.commit()

    if db.query(Item).count() == 0:
        admin = db.query(User).filter(User.username == "admin").first()
        for item in MOCK_ITEMS:
            db.add(Item(**item, created_by_id=admin.id if admin else None))
        db.commit()
