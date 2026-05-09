from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.auth_controller import router as auth_router
from controllers.job_controller import router as job_router
from controllers.job_application_controller import router as job_application_router
from db import init_db
from middleware.json_sanitizer import JSONSanitizerMiddleware

app = FastAPI(
    title="ATS API",
    description="Applicant Tracking System REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
init_db()

app.add_middleware(JSONSanitizerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(job_router)
app.include_router(job_application_router)

@app.get("/api/health")
def health():
    return {"status": "ok"}

