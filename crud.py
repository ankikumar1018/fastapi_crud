# crud.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Item
from schemas import ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/")
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_item = Item(**item.model_dump(), owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/")
def read_items(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Item).filter(Item.owner_id == current_user.id).all()


@router.get("/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}")
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}
