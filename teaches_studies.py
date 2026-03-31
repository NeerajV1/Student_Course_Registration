from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas import TeachesCreate, TeachesResponse, StudiesCreate, StudiesResponse

router = APIRouter(tags=["Teaches & Studies"])


# ── TEACHES ────────────────────────────────────────────
@router.post("/teaches/", response_model=TeachesResponse, status_code=201)
def assign_teacher_to_student(data: TeachesCreate, db: Session = Depends(get_db)):
    try:
        row = db.execute(
            text("INSERT INTO Teaches (TeacherId, StudentId) VALUES (:tid, :sid) RETURNING TeacherId, StudentId"),
            {"tid": data.TeacherId, "sid": data.StudentId}
        ).fetchone()
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="This teacher-student link already exists")
    m = dict(row._mapping)
    return {"TeacherId": m.get("teacherid"), "StudentId": m.get("studentid")}


@router.get("/teaches/", response_model=list[TeachesResponse])
def get_all_teaches(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT TeacherId, StudentId FROM Teaches")).fetchall()
    return [{"TeacherId": dict(r._mapping).get("teacherid"), "StudentId": dict(r._mapping).get("studentid")} for r in rows]


@router.get("/teaches/teacher/{teacher_id}", response_model=list[TeachesResponse])
def get_students_by_teacher(teacher_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT TeacherId, StudentId FROM Teaches WHERE TeacherId = :id"), {"id": teacher_id}
    ).fetchall()
    return [{"TeacherId": dict(r._mapping).get("teacherid"), "StudentId": dict(r._mapping).get("studentid")} for r in rows]


@router.delete("/teaches/{teacher_id}/{student_id}", status_code=204)
def remove_teacher_student_link(teacher_id: int, student_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM Teaches WHERE TeacherId = :tid AND StudentId = :sid"),
        {"tid": teacher_id, "sid": student_id}
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Link not found")
    db.commit()


# ── STUDIES ────────────────────────────────────────────
@router.post("/studies/", response_model=StudiesResponse, status_code=201)
def assign_student_to_course(data: StudiesCreate, db: Session = Depends(get_db)):
    try:
        row = db.execute(
            text("INSERT INTO Studies (StudentId, CourseId) VALUES (:sid, :cid) RETURNING StudentId, CourseId"),
            {"sid": data.StudentId, "cid": data.CourseId}
        ).fetchone()
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="This student-course link already exists")
    m = dict(row._mapping)
    return {"StudentId": m.get("studentid"), "CourseId": m.get("courseid")}


@router.get("/studies/", response_model=list[StudiesResponse])
def get_all_studies(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT StudentId, CourseId FROM Studies")).fetchall()
    return [{"StudentId": dict(r._mapping).get("studentid"), "CourseId": dict(r._mapping).get("courseid")} for r in rows]


@router.get("/studies/student/{student_id}", response_model=list[StudiesResponse])
def get_courses_by_student(student_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT StudentId, CourseId FROM Studies WHERE StudentId = :id"), {"id": student_id}
    ).fetchall()
    return [{"StudentId": dict(r._mapping).get("studentid"), "CourseId": dict(r._mapping).get("courseid")} for r in rows]


@router.delete("/studies/{student_id}/{course_id}", status_code=204)
def remove_studies_link(student_id: int, course_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM Studies WHERE StudentId = :sid AND CourseId = :cid"),
        {"sid": student_id, "cid": course_id}
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Link not found")
    db.commit()
