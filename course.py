from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas import CourseCreate, CourseResponse

router = APIRouter(prefix="/courses", tags=["Courses"])


def map_course(row) -> dict:
    m = dict(row._mapping)
    return {
        "CourseId":       m.get("courseid"),
        "CourseName":     m.get("coursename"),
        "Credit":         m.get("credit"),
        "CourseDuration": m.get("courseduration"),
        "Prerequisites":  m.get("prerequisites"),
    }


@router.post("/", response_model=CourseResponse, status_code=201)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    if not course.CourseName:
        raise HTTPException(status_code=400, detail="Course name is required")
    row = db.execute(
        text("""
            INSERT INTO Course (CourseName, Credit, CourseDuration, Prerequisites)
            VALUES (:name, :credit, :duration, :prereq)
            RETURNING CourseId, CourseName, Credit, CourseDuration, Prerequisites
        """),
        {"name": course.CourseName, "credit": course.Credit,
         "duration": course.CourseDuration, "prereq": course.Prerequisites}
    ).fetchone()
    db.commit()
    return map_course(row)


@router.get("/", response_model=list[CourseResponse])
def get_all_courses(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT CourseId, CourseName, Credit, CourseDuration, Prerequisites FROM Course")
    ).fetchall()
    return [map_course(r) for r in rows]


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT CourseId, CourseName, Credit, CourseDuration, Prerequisites FROM Course WHERE CourseId = :id"),
        {"id": course_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Course not found")
    return map_course(row)


@router.get("/{course_id}/students")
def get_students_in_course(course_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT s.StudentId, s.Email, s.Semester, r.DateOfRegistration
            FROM Registration r JOIN Student s ON r.StudentId = s.StudentId
            WHERE r.CourseId = :id
        """),
        {"id": course_id}
    ).fetchall()
    return [{"StudentId": dict(r._mapping).get("studentid"),
             "Email": dict(r._mapping).get("email"),
             "Semester": dict(r._mapping).get("semester"),
             "DateOfRegistration": dict(r._mapping).get("dateofregistration")} for r in rows]


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            UPDATE Course
            SET CourseName = :name, Credit = :credit,
                CourseDuration = :duration, Prerequisites = :prereq
            WHERE CourseId = :id
            RETURNING CourseId, CourseName, Credit, CourseDuration, Prerequisites
        """),
        {"name": course.CourseName, "credit": course.Credit,
         "duration": course.CourseDuration, "prereq": course.Prerequisites, "id": course_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Course not found")
    db.commit()
    return map_course(row)


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM Course WHERE CourseId = :id"),
        {"id": course_id}
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    db.commit()
