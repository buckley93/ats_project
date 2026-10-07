import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from models.jobs import Job, JobCreate, JobUpdate

logger = logging.getLogger(__name__)


def get_all_jobs(db: Session) -> list[Job]:
    try:
        jobs = db.query(Job).all()
        logger.info("Fetched %d jobs", len(jobs))
        return jobs
    except SQLAlchemyError as e:
        logger.error("Failed to fetch jobs: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs")

def get_job_by_id(job_id: int, db: Session) -> Job:
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        logger.info("Fetched job id=%d", job_id)
        return job
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Failed to fetch job id=%d: %s", job_id, e)
        raise HTTPException(status_code=500, detail="Failed to retrieve job")


def create_job(data: JobCreate, db: Session) -> Job:
    try:
        job = Job(job_description=data.job_description, job_link=data.job_link)
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info("Created job id=%d", job.job_id)
        return job
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to create job: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create job")


def update_job(job_id: int, data: JobUpdate, db: Session) -> Job:
    try:
        job = get_job_by_id(job_id, db)
        if data.job_description is not None:
            job.job_description = data.job_description
        if data.job_link is not None:
            job.job_link = data.job_link
        db.commit()
        db.refresh(job)
        logger.info("Updated job id=%d", job_id)
        return job
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to update job id=%d: %s", job_id, e)
        raise HTTPException(status_code=500, detail="Failed to update job")


def delete_job(job_id: int, db: Session) -> dict:
    try:
        job = get_job_by_id(job_id, db)
        db.delete(job)
        db.commit()
        logger.info("Deleted job id=%d", job_id)
        return {"message": f"Job {job_id} deleted"}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to delete job id=%d: %s", job_id, e)
        raise HTTPException(status_code=500, detail="Failed to delete job")
