# ATS Project

This is an Applicant Tracking System (ATS) project with:
- **Flask** backend (Python) for REST API, AI/ML modules, and MySQL integration
- **React** frontend for the user interface
- **MySQL** database for data storage

## Project Structure

```
ats_project/
├── backend/           # Flask backend
│   ├── app.py
│   ├── requirements.txt
│   └── .env.example
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


### 2. Backend (Flask)
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
cp .env.example .env  # Edit as needed
python app.py
```

### 3. Resume Recommendation API

Send a POST request to `/api/recommend_resume` with JSON:

```
{
	"job_description": "<job description text>",
	"resume": "<resume text>"
}
```

Response:
```
{
	"recommendations": ["...suggestions..."]
}
```

Example (using curl):
```
curl -X POST http://localhost:5000/api/recommend_resume \
	-H "Content-Type: application/json" \
	-d '{"job_description": "Python developer with Flask experience", "resume": "Experienced developer with Python"}'
```

### 3. Frontend (React)
```bash
cd frontend
npm install
npm start
```

### 4. Access
- Flask backend: http://localhost:5000/api/health
- React frontend: http://localhost:3000

---

**Note:**
- AI/ML modules and advanced features should be implemented in the backend (`backend/`).
- Update `.env` files with your actual configuration.
- This is a starter scaffold. Expand endpoints, models, and UI as needed.
