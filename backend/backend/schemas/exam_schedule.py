from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from ..models.enums import Subject


class ExamScheduleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    class_id: int
    subject: Subject
    exam_date: date
    start_time: str = Field(..., description="e.g. '09:00'")
    end_time: str = Field(..., description="e.g. '11:30'")
    location: str = Field(..., min_length=1, max_length=100)
    status: Optional[str] = "未开始"


class ExamScheduleResponse(BaseModel):
    id: int
    name: str
    class_id: int
    class_name: Optional[str] = None
    subject: Subject
    subject_name: Optional[str] = None
    exam_date: date
    start_time: str
    end_time: str
    location: str
    status: str

    class Config:
        from_attributes = True


class ConflictDetail(BaseModel):
    date: date
    class_id: int
    class_name: str
    exams: List[ExamScheduleResponse]
