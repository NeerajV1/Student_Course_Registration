from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas import TeacherCreate, TeacherResponse

router = APIRouter(prefix="/teachers", tags=["Teachers"])


def map_teacher(row) -> dict:
    m = dict(row._mapping)
    return {
        "TeacherId":       m.get("teacherid"),
        "TeacherName":     m.get("teachername"),
        "TeacherPhoneNo":  m.get("teacherphoneno"),
        "DeptId":          m.get("deptid"),
    }


@router.post("/", response_model=TeacherResponse, status_code=201)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            INSERT INTO Teacher (TeacherName, TeacherPhoneNo, DeptId)
            VALUES (:name, :phone, :dept)
            RETURNING TeacherId, TeacherName, TeacherPhoneNo, DeptId
        """),
        {"name": teacher.TeacherName, "phone": teacher.TeacherPhoneNo, "dept": teacher.DeptId}
    ).fetchone()
    db.commit()
    return map_teacher(row)


@router.get("/", response_model=list[TeacherResponse])
def get_all_teachers(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT TeacherId, TeacherName, TeacherPhoneNo, DeptId FROM Teacher")
    ).fetchall()
    return [map_teacher(r) for r in rows]


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT TeacherId, TeacherName, TeacherPhoneNo, DeptId FROM Teacher WHERE TeacherId = :id"),
        {"id": teacher_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return map_teacher(row)


@router.get("/department/{dept_id}", response_model=list[TeacherResponse])
def get_teachers_by_dept(dept_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT TeacherId, TeacherName, TeacherPhoneNo, DeptId FROM Teacher WHERE DeptId = :id"),
        {"id": dept_id}
    ).fetchall()
    return [map_teacher(r) for r in rows]


@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(teacher_id: int, teacher: TeacherCreate, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            UPDATE Teacher
            SET TeacherName = :name, TeacherPhoneNo = :phone, DeptId = :dept
            WHERE TeacherId = :id
            RETURNING TeacherId, TeacherName, TeacherPhoneNo, DeptId
        """),
        {"name": teacher.TeacherName, "phone": teacher.TeacherPhoneNo, "dept": teacher.DeptId, "id": teacher_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.commit()
    return map_teacher(row)


@router.delete("/{teacher_id}", status_code=204)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM Teacher WHERE TeacherId = :id"),
        {"id": teacher_id}
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.commit()
