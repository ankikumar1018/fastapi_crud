from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database, crud
from auth import router as auth_router, get_current_user

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FastAPI CRUD with Basic Auth")

# Include auth routes
app.include_router(auth_router)

# ----------------- CRUD ENDPOINTS -----------------
@app.post("/items/", response_model=schemas.Item)
def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_item(db=db, item=item, user_id=current_user.id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_items(db=db, user_id=current_user.id)


@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    updated_item = crud.update_item(db=db, item_id=item_id, item=item, user_id=current_user.id)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item


@app.delete("/items/{item_id}", response_model=schemas.Item)
def delete_item(item_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    deleted_item = crud.delete_item(db=db, item_id=item_id, user_id=current_user.id)
    if not deleted_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return deleted_item
