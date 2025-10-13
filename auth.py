# auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.hash import argon2
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import ChangePasswordRequest, UserCreate

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBasic()


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)
):
    """Authenticate user using Basic Auth."""
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not argon2.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Public signup endpoint — expects JSON { username, password }."""
    username = user.username
    password = user.password

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = argon2.hash(password)
    user = User(username=username, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created successfully", "username": username}


@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    """Protected endpoint — requires Basic Auth."""
    return {"username": current_user.username}


@router.put("/change-password")
def change_password(data: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not argon2.verify(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    current_user.hashed_password = argon2.hash(data.new_password)
    db.commit()
    db.refresh(current_user)
    return {"message": "Password updated successfully"}
