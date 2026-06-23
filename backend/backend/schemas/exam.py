from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class ExamCreate(BaseModel):
    name: str
    class_id: int
    exam_date: Optional[date] = None


class ExamResponse(BaseModel):
    id: int
    name: str
    class_id: int
    exam_date: Optional[str] = None
    created_at: Optional[str] = None


class ClassScoreItem(BaseModel):
    student_id: int
    student_name: str
    username: str  # 学号
    score: Optional[float] = None
    class_rank: Optional[int] = None
    school_rank: Optional[int] = None


class BatchScoreItem(BaseModel):
    student_id: int
    exam_id: int
    subject: str
    score: float


class ClassStatsResponse(BaseModel):
    exam_id: int
    exam_name: str
    subject: str
    avg_score: float
    max_score: float
    min_score: float
    pass_count: int
    total_count: int
    pass_rate: float
    excellent_count: int
    excellent_rate: float
    distribution: dict  # 分数段分布


class ClassDistribution(BaseModel):
    range_under_60: int
    range_60_69: int
    range_70_79: int
    range_80_89: int
    range_90_100: int
