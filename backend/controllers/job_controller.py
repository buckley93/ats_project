from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.jobs import JobCreate, JobUpdate, JobResponse
import services.job_service as job_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    return job_service.get_all_jobs(db)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    return job_service.get_job_by_id(job_id, db)


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(data: JobCreate, db: Session = Depends(get_db)):
    return job_service.create_job(data, db)


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, data: JobUpdate, db: Session = Depends(get_db)):
    return job_service.update_job(job_id, data, db)


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    return job_service.delete_job(job_id, db)
