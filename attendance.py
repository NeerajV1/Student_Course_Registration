from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas import (
    StudentAttendanceCreate, StudentAttendanceResponse,
    TeacherAttendanceCreate, TeacherAttendanceResponse
)

router = APIRouter(tags=["Attendance"])


def map_sa(row) -> dict:
    m = dict(row._mapping)
    return {
        "AttendanceId":   m.get("attendanceid"),
        "StudentId":      m.get("studentid"),
        "Day":            m.get("day"),
        "EntryTime":      m.get("entrytime"),
        "LeaveTime":      m.get("leavetime"),
        "Lecture":        m.get("lecture"),
        "EmergencyLeaves":m.get("emergencyleaves"),
        "Reason":         m.get("reason"),
    }


def map_ta(row) -> dict:
    m = dict(row._mapping)
    return {
        "AttendanceId":      m.get("attendanceid"),
        "TeacherId":         m.get("teacherid"),
        "Day":               m.get("day"),
        "EntryTime":         m.get("entrytime"),
        "LeaveTime":         m.get("leavetime"),
        "LecturesConducted": m.get("lecturesconducted"),
        "EmergencyLeaves":   m.get("emergencyleaves"),
        "Reason":            m.get("reason"),
    }


# ── STUDENT ATTENDANCE ─────────────────────────────────
@router.post("/attendance/student/", response_model=StudentAttendanceResponse, status_code=201)
def mark_student_attendance(data: StudentAttendanceCreate, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            INSERT INTO StudentAttendance
                (StudentId, Day, EntryTime, LeaveTime, Lecture, EmergencyLeaves, Reason)
            VALUES (:sid, :day, :entry, :leave, :lec, :emergency, :reason)
            RETURNING AttendanceId, StudentId, Day, EntryTime, LeaveTime, Lecture, EmergencyLeaves, Reason
        """),
        {"sid": data.StudentId, "day": data.Day, "entry": data.EntryTime,
         "leave": data.LeaveTime, "lec": data.Lecture,
         "emergency": data.EmergencyLeaves, "reason": data.Reason}
    ).fetchone()
    db.commit()
    return map_sa(row)


@router.get("/attendance/student/", response_model=list[StudentAttendanceResponse])
def get_all_student_attendance(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT AttendanceId, StudentId, Day, EntryTime, LeaveTime, Lecture, EmergencyLeaves, Reason FROM StudentAttendance")
    ).fetchall()
    return [map_sa(r) for r in rows]


@router.get("/attendance/student/{student_id}", response_model=list[StudentAttendanceResponse])
def get_student_attendance(student_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT AttendanceId, StudentId, Day, EntryTime, LeaveTime, Lecture, EmergencyLeaves, Reason
            FROM StudentAttendance WHERE StudentId = :id ORDER BY Day DESC
        """),
        {"id": student_id}
    ).fetchall()
    return [map_sa(r) for r in rows]


@router.delete("/attendance/student/{attendance_id}", status_code=204)
def delete_student_attendance(attendance_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM StudentAttendance WHERE AttendanceId = :id"), {"id": attendance_id}
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    db.commit()


# ── TEACHER ATTENDANCE ─────────────────────────────────
@router.post("/attendance/teacher/", response_model=TeacherAttendanceResponse, status_code=201)
def mark_teacher_attendance(data: TeacherAttendanceCreate, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            INSERT INTO TeacherAttendance
                (TeacherId, Day, EntryTime, LeaveTime, LecturesConducted, EmergencyLeaves, Reason)
            VALUES (:tid, :day, :entry, :leave, :lec, :emergency, :reason)
            RETURNING AttendanceId, TeacherId, Day, EntryTime, LeaveTime, LecturesConducted, EmergencyLeaves, Reason
        """),
        {"tid": data.TeacherId, "day": data.Day, "entry": data.EntryTime,
         "leave": data.LeaveTime, "lec": data.LecturesConducted,
         "emergency": data.EmergencyLeaves, "reason": data.Reason}
    ).fetchone()
    db.commit()
    return map_ta(row)


@router.get("/attendance/teacher/", response_model=list[TeacherAttendanceResponse])
def get_all_teacher_attendance(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT AttendanceId, TeacherId, Day, EntryTime, LeaveTime, LecturesConducted, EmergencyLeaves, Reason FROM TeacherAttendance")
    ).fetchall()
    return [map_ta(r) for r in rows]


@router.get("/attendance/teacher/{teacher_id}", response_model=list[TeacherAttendanceResponse])
def get_teacher_attendance(teacher_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT AttendanceId, TeacherId, Day, EntryTime, LeaveTime, LecturesConducted, EmergencyLeaves, Reason
            FROM TeacherAttendance WHERE TeacherId = :id ORDER BY Day DESC
        """),
        {"id": teacher_id}
    ).fetchall()
    return [map_ta(r) for r in rows]


@router.delete("/attendance/teacher/{attendance_id}", status_code=204)
def delete_teacher_attendance(attendance_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("DELETE FROM TeacherAttendance WHERE AttendanceId = :id"), {"id": attendance_id}
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    db.commit()
