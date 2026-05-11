import logging
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from models.user import User, registerRequest, userUpdate, createResume, updateResume, loginRequest
from fastapi import File
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
UPLOAD_DIR = "uploads/"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(username: str, password_hash: str, email: str, db: Session) -> User:
    try:
        existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        hashed_password = pwd_context.hash(password_hash[:72])
        user = User(username=username, password_hash=hashed_password, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Created user id=%d", user.user_id)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to create user: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create user")

def get_user_by_id(user_id: int, db: Session) -> User:
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info("Fetched user id=%d", user_id)
        return user
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Failed to fetch user id=%d: %s", user_id, e)
        raise HTTPException(status_code=500, detail="Failed to retrieve user")
    
def get_user_by_username(data: loginRequest, db: Session) -> User:
    try:
        user = db.query(User).filter(User.username == data.username).first()
        if not user or not pwd_context.verify(data.password[:72], user.password_hash):
            raise HTTPException(status_code=404, detail="User not found")
        logger.info("Fetched user username=%s", data.username)
        return {
        "message": "Login successful",
        "user_id": user.user_id,
        "access_token": f"fake-token-for-{user.username}"
    }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Failed to fetch user username=%s: %s", data.username, e)
        raise HTTPException(status_code=500, detail="Failed to retrieve user")
    
def get_all_users(db: Session) -> list[User]:
    try:
        users = db.query(User).all()
        logger.info("Fetched %d users", len(users))
        return users
    except SQLAlchemyError as e:
        logger.error("Failed to fetch users: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve users")
    
def update_user(user_id: int, data: File, db: Session) -> User:
    try:
        user = get_user_by_id(user_id, db)
        if data.username is not None:
            user.username = data.username
        if data.password_hash is not None:
            user.password_hash = data.password_hash
        db.commit()
        db.refresh(user)
        logger.info("Updated user id=%d", user_id)
        return user
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to update user id=%d: %s", user_id, e)
        raise HTTPException(status_code=500, detail="Failed to update user")

def delete_user(user_id: int, db: Session) -> dict:
    try:
        user = get_user_by_id(user_id, db)
        delete_files_with_name(user.username)
        db.delete(user)
        db.commit()
        logger.info("Deleted user id=%d", user_id)
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to delete user id=%d: %s", user_id, e)
        raise HTTPException(status_code=500, detail="Failed to delete user")
    
def create_resume(user_id: int, file: File, db: Session) -> User:
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        print(file)
        user = get_user_by_id(user_id, db)
        delete_files_with_name(user.username)
        file_location = os.path.join(UPLOAD_DIR, f"{user.username}_{file.filename}")
        with open(file_location, "wb") as f:
            f.write(file.file.read())  # Save the uploaded file
        user.resume_path = file_location
        db.commit()
        db.refresh(user)
        logger.info("Created resume for user id=%d", user_id)
        return user
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to create resume for user id=%d: %s", user_id, e)
        raise HTTPException(status_code=500, detail="Failed to create resume")

def delete_resume(user_id: int, db: Session) -> User:
    try:
        user = get_user_by_id(user_id, db)
        delete_files_with_name(user.username)
        user.resume_path = None
        db.commit()
        db.refresh(user)
        logger.info("Deleted resume for user id=%d", user_id)
        return user
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to delete resume for user id=%d: %s", user_id, e)
        raise HTTPException(status_code=500, detail="Failed to delete resume")
    
def delete_files_with_name(substring):
    try:
        for filename in os.listdir(UPLOAD_DIR):
            if substring in filename:
                file_path = os.path.join(UPLOAD_DIR, filename)
                os.remove(file_path)
                logger.info("Deleted file: %s", file_path)
    except OSError as e:
        logger.error("Failed to delete files with substring '%s': %s", substring, e)
        raise HTTPException(status_code=500, detail="Failed to delete files")

    
