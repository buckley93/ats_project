from fastapi import APIRouter, UploadFile, File, Form
from models.user import loginRequest, registerRequest, UserResponse, userUpdate
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends
from db import get_db
from services.user_service import create_user, get_user_by_id, get_all_users, update_user, get_user_by_username, create_resume, delete_user, delete_resume

router = APIRouter(prefix="/api/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=None)
async def register(data: registerRequest, db: Session = Depends(get_db)):
    return create_user(username=data.username, password_hash=data.password, email=data.email, db=db)

@router.post("/login", response_model=None)
async def login(data: loginRequest, db: Session = Depends(get_db)):
    return get_user_by_username(data, db)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return get_user_by_id(user_id, db)

@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)

@router.put("/{user_id}", response_model=UserResponse)
def update_user_info(user_id: int, data: userUpdate, db: Session = Depends(get_db)):
    return update_user(user_id, data, db)

@router.delete("/{user_id}")
def handle_delete_user(user_id: int, db: Session = Depends(get_db)):
    return delete_user(user_id, db)

@router.post("/upload_resume")
async def upload_resume( file: UploadFile = File(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    return create_resume(user_id, file, db)

@router.delete("/delete_resume/{user_id}")
def handle_delete_resume(user_id: int, db: Session = Depends(get_db)):
    return delete_resume(user_id, db)