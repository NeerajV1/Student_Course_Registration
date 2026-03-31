from pydantic import BaseModel, ConfigDict
from datetime import date, time
from typing import Optional


# -------------------------------------------------------
# Department
# -------------------------------------------------------

class DepartmentCreate(BaseModel):
    DeptName: str
    Location: Optional[str] = None

class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    DeptId: int
    DeptName: str
    Location: Optional[str] = None


# -------------------------------------------------------
# Teacher
# -------------------------------------------------------

class TeacherCreate(BaseModel):
    TeacherName: str
    TeacherPhoneNo: Optional[str] = None
    DeptId: int

class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    TeacherId: int
    TeacherName: str
    TeacherPhoneNo: Optional[str] = None
    DeptId: int


# -------------------------------------------------------
# Student
# -------------------------------------------------------

class StudentCreate(BaseModel):
    PhoneNo: Optional[str] = None
    Email: Optional[str] = None
    DOB: Optional[date] = None
    Semester: Optional[int] = None
    PrimaryCourseId: Optional[int] = None

class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    StudentId: int
    PhoneNo: Optional[str] = None
    Email: Optional[str] = None
    DOB: Optional[date] = None
    Semester: Optional[int] = None
    PrimaryCourseId: Optional[int] = None


# -------------------------------------------------------
# Course
# -------------------------------------------------------

class CourseCreate(BaseModel):
    CourseName: str
    Credit: Optional[int] = None
    CourseDuration: Optional[int] = None
    Prerequisites: Optional[str] = None

class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    CourseId: int
    CourseName: str
    Credit: Optional[int] = None
    CourseDuration: Optional[int] = None
    Prerequisites: Optional[str] = None


# -------------------------------------------------------
# Registration
# -------------------------------------------------------

class RegistrationCreate(BaseModel):
    StudentId: int
    CourseId: int

class RegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    RegistrationId: int
    StudentId: int
    CourseId: int
    DateOfRegistration: date


# -------------------------------------------------------
# Teaches  (Teacher <-> Student bridge)
# -------------------------------------------------------

class TeachesCreate(BaseModel):
    TeacherId: int
    StudentId: int

class TeachesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    TeacherId: int
    StudentId: int


# -------------------------------------------------------
# Studies  (Student <-> Course bridge)
# -------------------------------------------------------

class StudiesCreate(BaseModel):
    StudentId: int
    CourseId: int

class StudiesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    StudentId: int
    CourseId: int


# -------------------------------------------------------
# StudentAttendance
# -------------------------------------------------------

class StudentAttendanceCreate(BaseModel):
    StudentId: int
    Day: date
    EntryTime: Optional[time] = None
    LeaveTime: Optional[time] = None
    Lecture: Optional[str] = None
    EmergencyLeaves: Optional[bool] = False
    Reason: Optional[str] = None

class StudentAttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    AttendanceId: int
    StudentId: int
    Day: date
    EntryTime: Optional[time] = None
    LeaveTime: Optional[time] = None
    Lecture: Optional[str] = None
    EmergencyLeaves: Optional[bool] = None
    Reason: Optional[str] = None


# -------------------------------------------------------
# TeacherAttendance
# -------------------------------------------------------

class TeacherAttendanceCreate(BaseModel):
    TeacherId: int
    Day: date
    EntryTime: Optional[time] = None
    LeaveTime: Optional[time] = None
    LecturesConducted: Optional[int] = 0
    EmergencyLeaves: Optional[bool] = False
    Reason: Optional[str] = None

class TeacherAttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    AttendanceId: int
    TeacherId: int
    Day: date
    EntryTime: Optional[time] = None
    LeaveTime: Optional[time] = None
    LecturesConducted: Optional[int] = None
    EmergencyLeaves: Optional[bool] = None
    Reason: Optional[str] = None
