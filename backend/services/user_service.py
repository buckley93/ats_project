import logging
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from models.user import User, registerRequest, userUpdate, createResume, updateResume
from fastapi import File

logger = logging.getLogger(__name__)
UPLOAD_DIR = "uploads/"

def create_user(username: str, password_hash: str, email: str, db: Session) -> User:
    try:
        user = User(username=username, password_hash=password_hash, email=email)
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
    
def get_user_by_username(username: str, db: Session) -> User:
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info("Fetched user username=%s", username)
        return user
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Failed to fetch user username=%s: %s", username, e)
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

    
