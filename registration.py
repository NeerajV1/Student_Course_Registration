from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas import RegistrationCreate, RegistrationResponse

router = APIRouter(prefix="/registrations", tags=["Registrations"])


def map_reg(row) -> dict:
    m = dict(row._mapping)
    return {
        "RegistrationId":     m.get("registrationid"),
        "StudentId":          m.get("studentid"),
        "CourseId":           m.get("courseid"),
        "DateOfRegistration": m.get("dateofregistration"),
    }


@router.post("/", response_model=RegistrationResponse, status_code=201)
def register_student(reg: RegistrationCreate, db: Session = Depends(get_db)):
    student = db.execute(
        text("SELECT StudentId FROM Student WHERE StudentId = :id"), {"id": reg.StudentId}
    ).fetchone()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    course = db.execute(
        text("SELECT CourseId FROM Course WHERE CourseId = :id"), {"id": reg.CourseId}
    ).fetchone()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    try:
        row = db.execute(
            text("""
                INSERT INTO Registration (StudentId, CourseId)
                VALUES (:sid, :cid)
                RETURNING RegistrationId, StudentId, CourseId, DateOfRegistration
            """),
            {"sid": reg.StudentId, "cid": reg.CourseId}
        ).fetchone()
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Student already registered for this course")
    return map_reg(row)


@router.get("/", response_model=list[RegistrationResponse])
def get_all_registrations(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT RegistrationId, StudentId, CourseId, DateOfRegistration FROM Registration")
    ).fetchall()
    return [map_reg(r) for r in rows]


@router.get("/{registration_id}", response_model=RegistrationResponse)
def get_registration(registration_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT RegistrationId, StudentId, CourseId, DateOfRegistration FROM Registration WHERE RegistrationId = :id"),
        {"id": registration_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found")
    return map_reg(row)


@router.delete("/{registration_id}", status_code=204)
def delete_registration(registration_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM Registration WHERE RegistrationId = :id"), {"id": registration_id}
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registration not found")
    db.commit()
