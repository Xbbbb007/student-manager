from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from ..models.enums import Subject


class HomeworkCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    subject: Subject
    class_id: int
    due_date: datetime


class HomeworkResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    subject: Subject
    class_id: int
    class_name: Optional[str] = None
    teacher_id: int
    teacher_name: Optional[str] = None
    due_date: datetime
    created_at: datetime
    status: Optional[str] = None  # student-specific: "unsubmitted", "submitted", "graded"
    grade: Optional[Decimal] = None
    feedback: Optional[str] = None
    submission_id: Optional[int] = None
    submission_content: Optional[str] = None
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HomeworkSubmissionCreate(BaseModel):
    content: str = Field(..., min_length=1)


class HomeworkSubmissionResponse(BaseModel):
    id: int
    homework_id: int
    student_id: int
    student_name: Optional[str] = None
    student_username: Optional[str] = None
    content: str
    submitted_at: datetime
    grade: Optional[Decimal] = None
    feedback: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class HomeworkGradeRequest(BaseModel):
    grade: Decimal = Field(..., ge=0, le=100)
    feedback: Optional[str] = None


class HomeworkStatsDetail(BaseModel):
    homework_id: int
    title: str
    subject: str
    class_name: str
    total_students: int
    submitted_count: int
    graded_count: int
    submission_rate: float
    average_grade: Optional[float] = None
