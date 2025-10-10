from pydantic import BaseModel

# ----------------- Item Schemas -----------------
class ItemBase(BaseModel):
    name: str
    description: str
    price: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    class Config:
        orm_mode = True


# ----------------- User Schemas -----------------
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class ChangePassword(BaseModel):
    old_password: str
    new_password: str
