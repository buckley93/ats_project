# ATS Project


This is an Applicant Tracking System (ATS) project with:
- **FastAPI** backend (Python) for REST API and MySQL integration
- **React** frontend for the user interface
- **MySQL** database for data storage

## Project Structure

```
ats_project/
├── backend/           # FastAPI backend
│   ├── app.py
│   ├── requirements.txt
├── frontend/          # React frontend
│   ├── package.json
│   └── src/
│       ├── App.js
│       └── index.js
├── db/                # Database schema and scripts
│   └── init.sql
└── README.md
```

## Setup Instructions

### 1. MySQL Database
- Create a MySQL database using the script in `db/init.sql`.
- Update the `DATABASE_URI` in `backend/.env.example` and rename to `.env`.



### 2. Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
# Edit database connection in db.py if needed
uvicorn app:app --reload
```


### 3. Frontend (React)
```bash
cd frontend
npm install
npm start
```


### 4. Access
- FastAPI backend: http://localhost:8000/api/health
- React frontend: http://localhost:3000

---

**Note:**
- Authentication uses password hashing with bcrypt (see requirements.txt).
- Update database connection in `backend/db.py` as needed.
- This is a starter scaffold. Expand endpoints, models, and UI as needed.
