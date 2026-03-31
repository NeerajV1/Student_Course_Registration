from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas import StudentCreate, StudentResponse

router = APIRouter(prefix="/students", tags=["Students"])


def map_student(row) -> dict:
    m = dict(row._mapping)
    return {
        "StudentId":       m.get("studentid"),
        "PhoneNo":         m.get("phoneno"),
        "Email":           m.get("email"),
        "DOB":             m.get("dob"),
        "Semester":        m.get("semester"),
        "PrimaryCourseId": m.get("primarycourseid"),
    }


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            INSERT INTO Student (PhoneNo, Email, DOB, Semester, PrimaryCourseId)
            VALUES (:phone, :email, :dob, :sem, :course)
            RETURNING StudentId, PhoneNo, Email, DOB, Semester, PrimaryCourseId
        """),
        {
            "phone": student.PhoneNo,
            "email": student.Email,
            "dob":   student.DOB,
            "sem":   student.Semester,
            "course":student.PrimaryCourseId
        }
    ).fetchone()
    db.commit()
    return map_student(row)


@router.get("/", response_model=list[StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT StudentId, PhoneNo, Email, DOB, Semester, PrimaryCourseId FROM Student")
    ).fetchall()
    return [map_student(r) for r in rows]


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT StudentId, PhoneNo, Email, DOB, Semester, PrimaryCourseId FROM Student WHERE StudentId = :id"),
        {"id": student_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")
    return map_student(row)


@router.get("/{student_id}/courses")
def get_student_courses(student_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT c.CourseId, c.CourseName, c.Credit, r.DateOfRegistration
            FROM Registration r
            JOIN Course c ON r.CourseId = c.CourseId
            WHERE r.StudentId = :id
        """),
        {"id": student_id}
    ).fetchall()
    return [{"CourseId": dict(r._mapping).get("courseid"),
             "CourseName": dict(r._mapping).get("coursename"),
             "Credit": dict(r._mapping).get("credit"),
             "DateOfRegistration": dict(r._mapping).get("dateofregistration")} for r in rows]


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            UPDATE Student
            SET PhoneNo = :phone, Email = :email, DOB = :dob,
                Semester = :sem, PrimaryCourseId = :course
            WHERE StudentId = :id
            RETURNING StudentId, PhoneNo, Email, DOB, Semester, PrimaryCourseId
        """),
        {
            "phone": student.PhoneNo, "email": student.Email,
            "dob": student.DOB, "sem": student.Semester,
            "course": student.PrimaryCourseId, "id": student_id
        }
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")
    db.commit()
    return map_student(row)


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM Student WHERE StudentId = :id"),
        {"id": student_id}
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    db.commit()
