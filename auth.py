# auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.hash import argon2
from database import get_db
from models import User
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBasic()

# -----------------------
# 🔹 Utility Functions
# -----------------------

def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not argon2.verify(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Constant-time string comparison for extra safety
    if not secrets.compare_digest(credentials.username, user.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user


# -----------------------
# 🔹 Signup (Public)
# -----------------------

@router.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    """
    Public endpoint to create a new user.
    """
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = argon2.hash(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


# -----------------------
# 🔹 Get Current User (Protected)
# -----------------------

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns info about the current logged-in user.
    """
    return {"username": current_user.username}


# -----------------------
# 🔹 Change Password (Protected)
# -----------------------

@router.put("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Allows the current authenticated user to change their password.
    """
    if not argon2.verify(old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    current_user.password = argon2.hash(new_password)
    db.commit()
    db.refresh(current_user)
    return {"message": "Password updated successfully"}


# -----------------------
# 🔹 Delete User (Protected)
# -----------------------

@router.delete("/deleteuser/{username}")
def delete_user(username: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Allows an authenticated user to delete their own account.
    """
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="You can only delete your own account")

    db.delete(current_user)
    db.commit()
    return {"message": f"User '{username}' deleted successfully"}
