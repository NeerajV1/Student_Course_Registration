from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/departments", tags=["Departments"])


def map_dept(row) -> dict:
    m = dict(row._mapping)
    return {
        "DeptId":   m.get("deptid"),
        "DeptName": m.get("deptname"),
        "Location": m.get("location"),
    }


@router.post("/", response_model=DepartmentResponse, status_code=201)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            INSERT INTO Department (DeptName, Location)
            VALUES (:name, :loc)
            RETURNING DeptId, DeptName, Location
        """),
        {"name": dept.DeptName, "loc": dept.Location}
    ).fetchone()
    db.commit()
    return map_dept(row)


@router.get("/", response_model=list[DepartmentResponse])
def get_all_departments(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT DeptId, DeptName, Location FROM Department")).fetchall()
    return [map_dept(r) for r in rows]


@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT DeptId, DeptName, Location FROM Department WHERE DeptId = :id"),
        {"id": dept_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Department not found")
    return map_dept(row)


@router.put("/{dept_id}", response_model=DepartmentResponse)
def update_department(dept_id: int, dept: DepartmentCreate, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            UPDATE Department
            SET DeptName = :name, Location = :loc
            WHERE DeptId = :id
            RETURNING DeptId, DeptName, Location
        """),
        {"name": dept.DeptName, "loc": dept.Location, "id": dept_id}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Department not found")
    db.commit()
    return map_dept(row)


@router.delete("/{dept_id}", status_code=204)
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM Department WHERE DeptId = :id"),
        {"id": dept_id}
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Department not found")
    db.commit()
