from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Item, User
from app.schemas import MAX_QUANTITY, ItemCreate, ItemOut, ItemUpdate, StockAdjust

router = APIRouter(prefix="/api/items", tags=["items"])


def to_item_out(item: Item) -> ItemOut:
    data = ItemOut.model_validate(item)
    data.low_stock = item.quantity < item.min_stock
    return data


@router.get("", response_model=list[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items = db.query(Item).order_by(Item.name).all()
    return [to_item_out(i) for i in items]


@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return to_item_out(item)


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    body: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if db.query(Item).filter(Item.sku == body.sku).first():
        raise HTTPException(status_code=400, detail="SKU already exists")
    item = Item(**body.model_dump(), created_by_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_item_out(item)


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    body: ItemUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return to_item_out(item)


@router.post("/{item_id}/adjust", response_model=ItemOut)
def adjust_stock(
    item_id: int,
    body: StockAdjust,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    new_qty = item.quantity + body.delta
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    if new_qty > MAX_QUANTITY:
        raise HTTPException(status_code=400, detail="Quantity exceeds maximum allowed value")
    item.quantity = new_qty
    db.commit()
    db.refresh(item)
    return to_item_out(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
