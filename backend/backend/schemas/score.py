from pydantic import BaseModel
from typing import Optional, List


class ScoreItem(BaseModel):
    subject: str
    score: float
    class_rank: Optional[int] = None
    school_rank: Optional[int] = None


class ExamWithScores(BaseModel):
    exam_id: int
    exam_name: str
    exam_date: Optional[str] = None
    scores: List[ScoreItem]
    total: float
    class_rank: Optional[int] = None
    school_rank: Optional[int] = None


class StudentScoresResponse(BaseModel):
    student_id: int
    student_name: str
    class_name: str
    exams: List[ExamWithScores]


class ClassRankItem(BaseModel):
    rank: int
    student_id: int
    student_name: str
    total: float
    rank_change: Optional[int] = None
    score_change: Optional[float] = None


class ClassRankingResponse(BaseModel):
    exam_id: int
    exam_name: str
    rankings: List[ClassRankItem]
