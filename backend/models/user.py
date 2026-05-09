from typing import Optional
import re
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, field_validator
from db import Base


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    resume_path = Column(String(512), nullable=True)

def _sanitize_filename(cls, v: str) -> str:
        # Remove control and reserved characters
        v = re.sub(r'[\x00-\x1f\x7f\/\\:\*\?"<>\|]', '', v)
        # Strip leading/trailing whitespace and dots
        v = v.strip(' .')
        return v

class registerRequest(BaseModel):
    username: str
    password: str
    email: str

class loginRequest(BaseModel):
    username: str
    password: str
class userUpdate(BaseModel):
    username: Optional[str] = None
    password_hash: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    user_id: int
    username: str
    resume_path: Optional[str] = None

    class Config:
        from_attributes = True

class createResume(BaseModel):
    resume_path: str

    @field_validator("resume_path", mode="before")
    @classmethod
    def sanitize_filename(cls, v):
        return _sanitize_filename(cls, v)
    
class updateResume(BaseModel):
    resume_path: Optional[str] = None

    @field_validator("resume_path", mode="before")
    @classmethod
    def sanitize_filename(cls, v):
        return _sanitize_filename(cls, v) if v is not None else v

