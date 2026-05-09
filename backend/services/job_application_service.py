import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from models.job_application import JobApplication, JobApplicationCreate, JobApplicationUpdate

logger = logging.getLogger(__name__)


def get_all_applications(db: Session) -> list[JobApplication]:
    try:
        applications = db.query(JobApplication).all()
        logger.info("Fetched %d job applications", len(applications))
        return applications
    except SQLAlchemyError as e:
        logger.error("Failed to fetch job applications: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve job applications")


def get_application_by_id(job_application_id: int, db: Session) -> JobApplication:
    try:
        application = db.query(JobApplication).filter(
            JobApplication.job_application_id == job_application_id
        ).first()
        if not application:
            raise HTTPException(status_code=404, detail="Job application not found")
        logger.info("Fetched job application id=%d", job_application_id)
        return application
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error("Failed to fetch job application id=%d: %s", job_application_id, e)
        raise HTTPException(status_code=500, detail="Failed to retrieve job application")


def get_applications_by_user(user_id: int, db: Session) -> list[JobApplication]:
    try:
        applications = db.query(JobApplication).filter(
            JobApplication.user_id == user_id
        ).all()
        logger.info("Fetched %d applications for user_id=%d", len(applications), user_id)
        return applications
    except SQLAlchemyError as e:
        logger.error("Failed to fetch applications for user_id=%d: %s", user_id, e)
        raise HTTPException(status_code=500, detail="Failed to retrieve applications for user")


def get_applications_by_job(job_id: int, db: Session) -> list[JobApplication]:
    try:
        applications = db.query(JobApplication).filter(
            JobApplication.job_id == job_id
        ).all()
        logger.info("Fetched %d applications for job_id=%d", len(applications), job_id)
        return applications
    except SQLAlchemyError as e:
        logger.error("Failed to fetch applications for job_id=%d: %s", job_id, e)
        raise HTTPException(status_code=500, detail="Failed to retrieve applications for job")


def create_application(data: JobApplicationCreate, db: Session) -> JobApplication:
    try:
        application = JobApplication(
            user_id=data.user_id,
            job_id=data.job_id,
            ats_score=data.ats_score,
            ats_results=data.ats_results,
            analyzed_at=datetime.now(timezone.utc) if data.ats_score is not None else None,
            is_applied=data.is_applied,
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        logger.info("Created job application id=%d", application.job_application_id)
        return application
    except IntegrityError:
        db.rollback()
        logger.warning("Duplicate application attempt for user_id=%d job_id=%d", data.user_id, data.job_id)
        raise HTTPException(status_code=409, detail="Application already exists for this user and job")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to create job application: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create job application")


def update_application(job_application_id: int, data: JobApplicationUpdate, db: Session) -> JobApplication:
    try:
        application = get_application_by_id(job_application_id, db)
        if data.ats_score is not None:
            application.ats_score = data.ats_score
        if data.ats_results is not None:
            application.ats_results = data.ats_results
        if data.analyzed_at is not None:
            application.analyzed_at = data.analyzed_at
        if data.is_applied is not None:
            application.is_applied = data.is_applied
        db.commit()
        db.refresh(application)
        logger.info("Updated job application id=%d", job_application_id)
        return application
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to update job application id=%d: %s", job_application_id, e)
        raise HTTPException(status_code=500, detail="Failed to update job application")


def delete_application(job_application_id: int, db: Session) -> dict:
    try:
        application = get_application_by_id(job_application_id, db)
        db.delete(application)
        db.commit()
        logger.info("Deleted job application id=%d", job_application_id)
        return {"message": f"Job application {job_application_id} deleted"}
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to delete job application id=%d: %s", job_application_id, e)
        raise HTTPException(status_code=500, detail="Failed to delete job application")
