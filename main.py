from fastapi import FastAPI
from routes import department, teacher, student, course, registration, teaches_studies, attendance
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="Student Course Registration System",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(department.router)
app.include_router(teacher.router)
app.include_router(student.router)
app.include_router(course.router)
app.include_router(registration.router)
app.include_router(teaches_studies.router)
app.include_router(attendance.router)


@app.get("/")
def root():
    return {"message": "Student Course Registration API is running"}
