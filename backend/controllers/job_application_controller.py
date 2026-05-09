from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.job_application import JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse
import services.job_application_service as job_application_service

router = APIRouter(prefix="/api/job-applications", tags=["job-applications"])


@router.get("/", response_model=list[JobApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    return job_application_service.get_all_applications(db)


@router.get("/{job_application_id}", response_model=JobApplicationResponse)
def get_application(job_application_id: int, db: Session = Depends(get_db)):
    return job_application_service.get_application_by_id(job_application_id, db)


@router.get("/user/{user_id}", response_model=list[JobApplicationResponse])
def list_applications_by_user(user_id: int, db: Session = Depends(get_db)):
    return job_application_service.get_applications_by_user(user_id, db)


@router.get("/job/{job_id}", response_model=list[JobApplicationResponse])
def list_applications_by_job(job_id: int, db: Session = Depends(get_db)):
    return job_application_service.get_applications_by_job(job_id, db)


@router.post("/", response_model=JobApplicationResponse, status_code=201)
def create_application(data: JobApplicationCreate, db: Session = Depends(get_db)):
    return job_application_service.create_application(data, db)


@router.put("/{job_application_id}", response_model=JobApplicationResponse)
def update_application(job_application_id: int, data: JobApplicationUpdate, db: Session = Depends(get_db)):
    return job_application_service.update_application(job_application_id, data, db)


@router.delete("/{job_application_id}")
def delete_application(job_application_id: int, db: Session = Depends(get_db)):
    return job_application_service.delete_application(job_application_id, db)
