import random
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.teaching import Question, ExamPaper, Resource
from ..models.staff import Staff
from ..schemas.teaching import (
    QuestionCreate,
    QuestionResponse,
    ExamPaperCreate,
    ExamPaperResponse,
    ResourceCreate,
    ResourceResponse,
)
from ..schemas.user import ApiResponse
from .attendance import get_current_staff

router = APIRouter(prefix="/api/v1/teaching", tags=["教学增强"])

# ─── 题库管理 ──────────────────────────────────────────────────

@router.get("/questions")
def get_questions(
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_staff),
):
    """获取并筛选试题"""
    query = db.query(Question)
    if subject:
        query = query.filter(Question.subject == subject)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if question_type:
        query = query.filter(Question.question_type == question_type)
    
    questions = query.all()
    
    data = []
    for q in questions:
        # Get creator name
        creator = db.query(Staff).filter(Staff.id == q.created_by).first()
        data.append({
            "id": q.id,
            "subject": q.subject,
            "question_type": q.question_type,
            "question_desc": q.question_desc,
            "difficulty": q.difficulty,
            "answer": q.answer,
            "explanation": q.explanation,
            "created_by": q.created_by,
            "creator_name": creator.name if creator else "未知教师"
        })
    return ApiResponse(data=data)


@router.post("/questions")
def create_question(
    body: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_staff),
):
    """录入新试题"""
    q = Question(
        subject=body.subject,
        question_type=body.question_type,
        question_desc=body.question_desc,
        difficulty=body.difficulty,
        answer=body.answer,
        explanation=body.explanation,
        created_by=current_user.id
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return ApiResponse(message="试题录入成功", data={"id": q.id})


# ─── 出卷组卷 ──────────────────────────────────────────────────

@router.get("/papers")
def get_papers(
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_staff),
):
    """获取试卷列表"""
    query = db.query(ExamPaper)
    if subject:
        query = query.filter(ExamPaper.subject == subject)
    
    papers = query.order_by(ExamPaper.created_at.desc()).all()
    data = []
    for p in papers:
        creator = db.query(Staff).filter(Staff.id == p.created_by).first()
        data.append({
            "id": p.id,
            "title": p.title,
            "subject": p.subject,
            "difficulty": p.difficulty,
            "questions": p.questions,
            "created_by": p.created_by,
            "creator_name": creator.name if creator else "未知教师",
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return ApiResponse(data=data)


@router.post("/papers")
def create_paper(
    body: ExamPaperCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_staff),
):
    """手动或自动组卷"""
    # Verify questions exist
    for q_id in body.questions:
        exists = db.query(Question).filter(Question.id == q_id).first()
        if not exists:
            raise HTTPException(400, detail=f"试题 ID {q_id} 不存在")
            
    p = ExamPaper(
        title=body.title,
        subject=body.subject,
        difficulty=body.difficulty,
        questions=body.questions,
        created_by=current_user.id
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return ApiResponse(message="试卷组卷成功", data={"id": p.id})


@router.post("/papers/auto")
def auto_generate_paper(
    title: str,
    subject: str,
    difficulty: str,
    count: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_staff),
):
    """智能自动组卷"""
    # Find matching questions
    matching_q = db.query(Question).filter(
        Question.subject == subject,
        Question.difficulty == difficulty
    ).all()
    
    if len(matching_q) < count:
        raise HTTPException(400, detail=f"题库中符合学科及难度要求的题目不足（当前仅有 {len(matching_q)} 道，要求 {count} 道）")
        
    selected_qs = random.sample(matching_q, count)
    q_ids = [q.id for q in selected_qs]
    
    p = ExamPaper(
        title=title,
        subject=subject,
        difficulty=difficulty,
        questions=q_ids,
        created_by=current_user.id
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return ApiResponse(message="智能自动组卷成功", data={"id": p.id, "questions": q_ids})


# ─── 教学资源库 ───────────────────────────────────────────────

@router.get("/resources")
def get_resources(
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_staff),
):
    """获取资源文件列表"""
    query = db.query(Resource)
    if subject:
        query = query.filter(Resource.subject == subject)
    if grade:
        query = query.filter(Resource.grade == grade)
        
    resources = query.order_by(Resource.created_at.desc()).all()
    data = []
    for r in resources:
        uploader = db.query(Staff).filter(Staff.id == r.upload_by).first()
        data.append({
            "id": r.id,
            "title": r.title,
            "subject": r.subject,
            "grade": r.grade,
            "file_name": r.file_name,
            "file_path": r.file_path,
            "upload_by": r.upload_by,
            "uploader_name": uploader.name if uploader else "未知教师",
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return ApiResponse(data=data)


@router.post("/resources")
def upload_resource(
    body: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_staff),
):
    """添加/上传教案课件资源信息"""
    r = Resource(
        title=body.title,
        subject=body.subject,
        grade=body.grade,
        file_name=body.file_name,
        file_path=body.file_path,
        upload_by=current_user.id
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return ApiResponse(message="资源上传成功", data={"id": r.id})
