from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from db import Base

class RegisterRequest(BaseModel):
    username: str
    password: str

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    resume_path = Column(String(512), nullable=True)
