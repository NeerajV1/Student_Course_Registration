from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:2662@localhost/Student_Course_Registration")

engine = create_engine(DATABASE_URL)

sessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
