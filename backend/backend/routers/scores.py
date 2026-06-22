from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List
from datetime import date

from ..database import get_db
from ..models.student import Student
from ..models.class_model import Class
from ..models.exam import Exam
from ..models.score import Score
from ..models.enums import Subject
from ..schemas.score import (
    StudentScoresResponse,
    ExamWithScores,
    ScoreItem,
    ClassRankingResponse,
    ClassRankItem,
)
from ..schemas.user import ApiResponse
from ..core.security import decode_access_token

SUBJECT_MAP = {
    "chinese": "语文",
    "math": "数学",
    "english": "英语",
    "science": "科学",
    "ethics": "道德与法治",
}

SUBJECT_KEYS = ["chinese", "math", "english", "science", "ethics"]

router = APIRouter(prefix="/api/v1/scores", tags=["成绩管理"])


def get_current_student(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> Student:
    if not authorization:
        raise HTTPException(401, detail="缺少认证信息")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, detail="Token 格式错误")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(401, detail="Token 无效")
    user_type = payload.get("user_type", "staff")
    if user_type != "student":
        raise HTTPException(403, detail="仅学生可执行此操作")
    user_id = int(payload.get("sub", 0))
    user = db.query(Student).filter(Student.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="学生不存在")
    return user


@router.get("/my", response_model=ApiResponse)
def get_my_scores(
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    class_obj = db.query(Class).filter(Class.id == current_user.class_id).first()
    class_name = class_obj.name if class_obj else ""

    exams = (
        db.query(Exam)
        .filter(Exam.class_id == current_user.class_id)
        .order_by(Exam.exam_date.asc())
        .all()
    )

    exam_list: List[ExamWithScores] = []
    for exam in exams:
        scores = (
            db.query(Score)
            .filter(Score.student_id == current_user.id, Score.exam_id == exam.id)
            .all()
        )
        score_items = []
        total = 0.0
        for s in scores:
            score_items.append(
                ScoreItem(
                    subject=s.subject,
                    score=s.score,
                    class_rank=s.class_rank,
                    school_rank=s.school_rank,
                )
            )
            total += s.score

        total_rank = (
            db.query(Score.class_rank)
            .filter(Score.exam_id == exam.id, Score.subject == Subject.CHINESE)
            .first()
        )

        exam_list.append(
            ExamWithScores(
                exam_id=exam.id,
                exam_name=exam.name,
                exam_date=str(exam.exam_date) if exam.exam_date else None,
                scores=score_items,
                total=round(total, 1),
            )
        )

    return ApiResponse(
        data=StudentScoresResponse(
            student_id=current_user.id,
            student_name=current_user.name,
            class_name=class_name,
            exams=exam_list,
        ).model_dump()
    )


@router.get("/ranking/{exam_id}", response_model=ApiResponse)
def get_class_ranking(
    exam_id: int,
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(404, detail="考试不存在")

    subtotals = (
        db.query(
            Score.student_id,
            sql_func.sum(Score.score).label("total"),
        )
        .filter(Score.exam_id == exam_id)
        .group_by(Score.student_id)
        .order_by(sql_func.sum(Score.score).desc())
        .all()
    )

    prev_exam = (
        db.query(Exam)
        .filter(Exam.class_id == exam.class_id, Exam.exam_date < exam.exam_date)
        .order_by(Exam.exam_date.desc())
        .first()
    )

    prev_totals = {}
    if prev_exam:
        prev_rows = (
            db.query(
                Score.student_id,
                sql_func.sum(Score.score).label("total"),
            )
            .filter(Score.exam_id == prev_exam.id)
            .group_by(Score.student_id)
            .all()
        )
        prev_totals = {sid: t for sid, t in prev_rows}

    prev_ranking = sorted(prev_totals.items(), key=lambda x: x[1], reverse=True)
    prev_rank_map = {sid: rank + 1 for rank, (sid, _) in enumerate(prev_ranking)}

    rankings: List[ClassRankItem] = []
    student_ids = [sid for sid, _ in subtotals]
    student_names = {
        s.id: s.name
        for s in db.query(Student).filter(Student.id.in_(student_ids)).all()
    }

    for rank, (sid, total) in enumerate(subtotals, 1):
        rank_change = None
        score_change = None
        if sid in prev_rank_map:
            rank_change = prev_rank_map[sid] - rank
        if sid in prev_totals:
            score_change = round(total - prev_totals[sid], 1)

        rankings.append(
            ClassRankItem(
                rank=rank,
                student_id=sid,
                student_name=student_names.get(sid, ""),
                total=round(total, 1),
                rank_change=rank_change,
                score_change=score_change,
            )
        )

    return ApiResponse(
        data=ClassRankingResponse(
            exam_id=exam.id,
            exam_name=exam.name,
            rankings=rankings,
        ).model_dump()
    )


@router.get("/trend", response_model=ApiResponse)
def get_score_trend(
    current_user: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    exams = (
        db.query(Exam)
        .filter(Exam.class_id == current_user.class_id)
        .order_by(Exam.exam_date.asc())
        .all()
    )

    result = {
        "exam_labels": [],
        "scores": {k: [] for k in SUBJECT_KEYS},
        "total_scores": [],
        "class_rank": [],
        "school_rank": [],
        "subject_class_ranks": {k: [] for k in SUBJECT_KEYS},
        "subject_school_ranks": {k: [] for k in SUBJECT_KEYS},
    }

    for exam in exams:
        result["exam_labels"].append(exam.name)

        exam_scores = (
            db.query(Score)
            .filter(Score.student_id == current_user.id, Score.exam_id == exam.id)
            .all()
        )
        score_map = {s.subject: s for s in exam_scores}

        total = 0
        for key in SUBJECT_KEYS:
            s = score_map.get(Subject(key))
            if s:
                result["scores"][key].append(s.score)
                result["subject_class_ranks"][key].append(s.class_rank)
                result["subject_school_ranks"][key].append(s.school_rank)
                total += s.score
            else:
                result["scores"][key].append(0)
                result["subject_class_ranks"][key].append(None)
                result["subject_school_ranks"][key].append(None)

        result["total_scores"].append(round(total, 1))

        first_score = exam_scores[0] if exam_scores else None
        result["class_rank"].append(first_score.class_rank if first_score else None)
        result["school_rank"].append(first_score.school_rank if first_score else None)

    class_obj = db.query(Class).filter(Class.id == current_user.class_id).first()

    return ApiResponse(data={
        **result,
        "student_id": current_user.id,
        "student_name": current_user.name,
        "student_no": current_user.username,
        "class_name": class_obj.name if class_obj else "",
    })
