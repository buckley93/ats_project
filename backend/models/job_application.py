from sqlalchemy import Column, Integer, Numeric, JSON, DateTime, Boolean, ForeignKey, UniqueConstraint, func
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from decimal import Decimal
from db import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    job_application_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=False)
    ats_score = Column(Numeric(precision=5, scale=2), nullable=True)
    ats_results = Column(JSON, nullable=True)
    analyzed_at = Column(DateTime, nullable=True, default=func.now())
    is_applied = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job"),
    )


class JobApplicationCreate(BaseModel):
    user_id: int
    job_id: int
    ats_score: Optional[Decimal] = None
    ats_results: Optional[Any] = None
    is_applied: bool = False


class JobApplicationUpdate(BaseModel):
    ats_score: Optional[Decimal] = None
    ats_results: Optional[Any] = None
    analyzed_at: Optional[datetime] = None
    is_applied: Optional[bool] = None


class JobApplicationResponse(BaseModel):
    job_application_id: int
    user_id: int
    job_id: int
    ats_score: Optional[Decimal]
    ats_results: Optional[Any]
    analyzed_at: Optional[datetime]
    is_applied: bool

    class Config:
        from_attributes = True
