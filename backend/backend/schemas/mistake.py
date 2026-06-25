from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from ..models.enums import Subject


class MistakeCreate(BaseModel):
    subject: Subject
    question_desc: str = Field(..., min_length=1)
    my_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    exam_id: Optional[int] = None
    test_id: Optional[int] = None


class MistakeResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    subject: Subject
    subject_name: Optional[str] = None
    question_desc: str
    my_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    is_mastered: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MistakeSubjectStat(BaseModel):
    subject: str
    subject_name: str
    count: int
    mastered_count: int


class MistakeStatsResponse(BaseModel):
    total: int
    mastered: int
    active: int
    mastered_rate: float
    by_subject: List[MistakeSubjectStat]
