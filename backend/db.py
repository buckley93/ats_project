from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set your database URI directly here
DATABASE_URI = "mysql://root:root@localhost/ats_db"
engine = create_engine(DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
