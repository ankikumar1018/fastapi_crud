from typing import Optional

from pydantic import BaseModel, ConfigDict


# --- Item Schemas ---
class ItemBase(BaseModel):
    name: str
    description: str
    price: int

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None

class Item(ItemBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes = True)


# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes = True)

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

