from fastapi import APIRouter, HTTPException
from models.user import RegisterRequest, User
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends
from db import get_db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/api/register")
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    # Debug: print password lengths
    print("Password length:", len(data.password))
    print("Truncated password length:", len(data.password[:72]))
    # Truncate password to 72 characters for bcrypt
    hashed_password = pwd_context.hash(data.password[:72])
    user = User(username=data.username, password_hash=hashed_password, role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully"}

@router.post("/api/login")
async def login(data: RegisterRequest, db: Session = Depends(get_db)):
    print("Login attempt:", data.username, data.password)
    user = db.query(User).filter(User.username == data.username).first()
    print("User from DB:", user)
    if not user or not pwd_context.verify(data.password[:72], user.password_hash):
        print("Login failed: invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    print("Login successful")
    # Return a fake access_token for frontend compatibility
    return {
        "message": "Login successful",
        "user_id": user.user_id,
        "role": user.role,
        "access_token": f"fake-token-for-{user.username}"
    }
