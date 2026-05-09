from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from models.user import loginRequest, registerRequest, User, UserResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends
from db import get_db
from services.user_service import create_user, get_user_by_id, get_all_users, update_user, get_user_by_username, create_resume

router = APIRouter(prefix="/api/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=None)
async def register(data: registerRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == data.username).first() or db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    # Debug: print password lengths
    print("Password length:", len(data.password))
    print("Truncated password length:", len(data.password[:72]))
    # Truncate password to 72 characters for bcrypt
    hashed_password = pwd_context.hash(data.password[:72])
    create_user(
        username=data.username,
        password_hash=hashed_password,
        email=data.email,
        db=db
    )
    return {"message": "User registered successfully"}

@router.post("/login", response_model=None)
async def login(data: loginRequest, db: Session = Depends(get_db)):
    print("Login attempt:", data.username, data.password)
    user = get_user_by_username(data.username, db)
    print("User from DB:", user)
    if not user or not pwd_context.verify(data.password[:72], user.password_hash):
        print("Login failed: invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    print("Login successful")
    # Return a fake access_token for frontend compatibility
    return {
        "message": "Login successful",
        "user_id": user.user_id,
        "access_token": f"fake-token-for-{user.username}"
    }

@router.post("/upload_resume")
async def upload_resume( file: UploadFile = File(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    print("Received file:", file.filename)
    print("User ID:", user_id)
    create_resume(user_id, file, db)
    return {"message": "Resume uploaded successfully"}