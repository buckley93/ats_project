import re
from sqlalchemy import Column, Integer, String, Text
from pydantic import BaseModel, field_validator
from typing import Optional
from db import Base


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    job_description = Column(Text, nullable=False)
    job_link = Column(String(2048), nullable=False)


def _strip_control_chars(v: str) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", v)


class JobCreate(BaseModel):
    job_description: str
    job_link: str

    @field_validator("job_description", "job_link", mode="before")
    @classmethod
    def sanitize(cls, v):
        return _strip_control_chars(v)


class JobUpdate(BaseModel):
    job_description: Optional[str] = None
    job_link: Optional[str] = None

    @field_validator("job_description", "job_link", mode="before")
    @classmethod
    def sanitize(cls, v):
        return _strip_control_chars(v) if v is not None else v


class JobResponse(BaseModel):
    job_id: int
    job_description: str
    job_link: str

    class Config:
        from_attributes = True
