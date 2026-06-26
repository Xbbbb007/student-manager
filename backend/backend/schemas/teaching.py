from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuestionCreate(BaseModel):
    subject: str
    question_type: str
    question_desc: str
    difficulty: str
    answer: Optional[str] = None
    explanation: Optional[str] = None

class QuestionResponse(BaseModel):
    id: int
    subject: str
    question_type: str
    question_desc: str
    difficulty: str
    answer: Optional[str]
    explanation: Optional[str]
    created_by: int
    creator_name: Optional[str] = None

    class Config:
        orm_mode = True

class ExamPaperCreate(BaseModel):
    title: str
    subject: str
    difficulty: str
    questions: List[int]

class ExamPaperResponse(BaseModel):
    id: int
    title: str
    subject: str
    difficulty: str
    questions: List[int]
    created_by: int
    created_at: datetime
    creator_name: Optional[str] = None

    class Config:
        orm_mode = True

class ResourceCreate(BaseModel):
    title: str
    subject: str
    grade: str
    file_name: str
    file_path: str

class ResourceResponse(BaseModel):
    id: int
    title: str
    subject: str
    grade: str
    file_name: str
    file_path: str
    upload_by: int
    created_at: datetime
    uploader_name: Optional[str] = None

    class Config:
        orm_mode = True
