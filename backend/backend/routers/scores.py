"""
成绩管理路由 — 学生端 + 教师端
"""
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
from ..models.staff import Staff
from ..models.enums import Subject, StaffRole
from ..schemas.score import (
    StudentScoresResponse, ExamWithScores, ScoreItem,
    ClassRankingResponse, ClassRankItem,
)
from ..schemas.user import ApiResponse
from ..core.security import decode_access_token
from ..services.auth import get_staff_by_id

SUBJECT_MAP = {
    "chinese": "语文",
    "math": "数学",
    "english": "英语",
    "science": "科学",
    "ethics": "道德与法治",
}
SUBJECT_KEYS = ["chinese", "math", "english", "science", "ethics"]

router = APIRouter(prefix="/api/v1/scores", tags=["成绩管理"])


# ═══════════════════════════════════════════════════════
# 通用依赖
# ═══════════════════════════════════════════════════════

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


def get_current_teacher(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> Staff:
    """获取当前登录的教职工（教师或管理员）"""
    if not authorization:
        raise HTTPException(401, detail="缺少认证信息")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, detail="Token 格式错误")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(401, detail="Token 无效")
    user_type = payload.get("user_type", "staff")
    if user_type != "staff":
        raise HTTPException(403, detail="仅教职工可执行此操作")
    user = get_staff_by_id(db, int(payload.get("sub", 0)))
    if not user:
        raise HTTPException(404, detail="用户不存在")
    return user


# ─── Helper: 权限检查 ───────────────────────────────

def _can_manage_subject(teacher: Staff, class_obj: Class, subject_key: str) -> bool:
    """判断教师是否有权管理该科目的成绩"""
    # 管理员可以管理所有科目
    if teacher.role == StaffRole.ADMIN:
        return True
    # 班主任可以管理本班所有科目
    if class_obj.homeroom_teacher_id == teacher.id:
        return True
    # 科任老师只能管理自己科目的成绩
    if teacher.subject and teacher.subject.value == subject_key:
        return True
    return False


def _recalc_ranks(db: Session, exam_id: int, class_id: int):
    """重新计算指定考试+班级的排名"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        return

    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        return

    # 获取同年级的所有班级
    same_grade = db.query(Class.id).filter(
        Class.section == class_obj.section,
        Class.grade == class_obj.grade,
    ).all()
    same_grade_ids = [c.id for c in same_grade]

    # 对每个科目重算排名
    for key in SUBJECT_KEYS:
        subject = Subject(key)

        # 校内排名 (年级排名)
        school_scores = db.query(
            Score.id,
            Score.student_id,
            Score.score,
        ).filter(
            Score.exam_id == exam_id,
            Score.subject == subject,
        ).join(Student, Student.id == Score.student_id).filter(
            Student.class_id.in_(same_grade_ids),
        ).order_by(Score.score.desc()).all()

        # DENSE_RANK 逻辑
        current_rank = 0
        prev_score = None
        for idx, (sid, stu_id, sc) in enumerate(school_scores, 1):
            if prev_score is None or sc < prev_score:
                current_rank = idx
            prev_score = sc
            db.query(Score).filter(Score.id == sid).update(
                {"school_rank": current_rank}
            )

        # 班内排名
        class_scores = db.query(
            Score.id, Score.score
        ).filter(
            Score.exam_id == exam_id,
            Score.subject == subject,
        ).join(Student, Student.id == Score.student_id).filter(
            Student.class_id == class_id,
        ).order_by(Score.score.desc()).all()

        current_rank = 0
        prev_score = None
        for idx, (sid, sc) in enumerate(class_scores, 1):
            if prev_score is None or sc < prev_score:
                current_rank = idx
            prev_score = sc
            db.query(Score).filter(Score.id == sid).update(
                {"class_rank": current_rank}
            )

    db.commit()


# ═══════════════════════════════════════════════════════
# 学生端 API（已有，保持兼容）
# ═══════════════════════════════════════════════════════

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
        .join(Student, Student.id == Score.student_id)
        .filter(Score.exam_id == exam_id, Student.class_id == current_user.class_id)
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
            .join(Student, Student.id == Score.student_id)
            .filter(Score.exam_id == prev_exam.id, Student.class_id == current_user.class_id)
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
    latest_exam_id = exams[-1].id if exams else None

    return ApiResponse(data={
        **result,
        "student_id": current_user.id,
        "student_name": current_user.name,
        "student_no": current_user.username,
        "class_name": class_obj.name if class_obj else "",
        "latest_exam_id": latest_exam_id,
    })


# ═══════════════════════════════════════════════════════
# 教师端 API
# ═══════════════════════════════════════════════════════

@router.get("/class-scores")
def get_class_scores(
    exam_id: int,
    subject: str,
    class_id: Optional[int] = None,
    current_user: Staff = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """教师端：获取某班级某次考试某科目的成绩列表"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(404, detail="考试不存在")

    if class_id is None:
        class_id = exam.class_id
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(404, detail="班级不存在")

    # 权限检查
    if not _can_manage_subject(current_user, class_obj, subject):
        raise HTTPException(403, detail=f"您无权管理{SUBJECT_MAP.get(subject, subject)}成绩")

    students = (
        db.query(Student)
        .filter(Student.class_id == class_id)
        .order_by(Student.id.asc())
        .all()
    )

    scores = (
        db.query(Score)
        .filter(
            Score.exam_id == exam_id,
            Score.subject == Subject(subject),
        )
        .all()
    )
    score_map = {s.student_id: s for s in scores}

    data = []
    for stu in students:
        s = score_map.get(stu.id)
        data.append({
            "student_id": stu.id,
            "student_name": stu.name,
            "username": stu.username,
            "score": s.score if s else None,
            "class_rank": s.class_rank if s else None,
            "school_rank": s.school_rank if s else None,
        })

    return ApiResponse(data={
        "exam_id": exam.id,
        "exam_name": exam.name,
        "class_id": class_obj.id,
        "class_name": class_obj.name,
        "subject": subject,
        "students": data,
    })


@router.put("/batch")
def batch_update_scores(
    body: dict,
    current_user: Staff = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """教师端：批量更新/录入成绩"""
    items = body.get("items", [])
    if not items:
        raise HTTPException(400, detail="成绩列表为空")

    # 收集需要重算排名的考试+班级
    exam_ids = set()
    class_ids = set()

    processed = 0
    for item in items:
        student_id = item.get("student_id")
        exam_id = item.get("exam_id")
        subject = item.get("subject")
        score_val = item.get("score")

        if not all([student_id, exam_id, subject, score_val is not None]):
            continue

        # 权限检查
        class_obj = (
            db.query(Class)
            .join(Student, Student.class_id == Class.id)
            .filter(Student.id == student_id)
            .first()
        )
        if not class_obj:
            continue
        if not _can_manage_subject(current_user, class_obj, subject):
            raise HTTPException(403, detail=f"您无权修改{class_obj.name}的{SUBJECT_MAP.get(subject, subject)}成绩")

        exam_ids.add(exam_id)
        class_ids.add(class_obj.id)

        existing = (
            db.query(Score)
            .filter(
                Score.student_id == student_id,
                Score.exam_id == exam_id,
                Score.subject == Subject(subject),
            )
            .first()
        )

        if existing:
            existing.score = score_val
        else:
            new_score = Score(
                student_id=student_id,
                exam_id=exam_id,
                subject=Subject(subject),
                score=score_val,
            )
            db.add(new_score)

        processed += 1

    db.commit()

    # 重算排名
    for eid in exam_ids:
        for cid in class_ids:
            _recalc_ranks(db, eid, cid)

    return ApiResponse(message=f"成功保存{processed}条成绩，排名已更新")


@router.get("/class-stats/{exam_id}")
def get_class_stats(
    exam_id: int,
    current_user: Staff = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """教师端：获取指定考试的班级统计"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(404, detail="考试不存在")

    class_obj = db.query(Class).filter(Class.id == exam.class_id).first()
    if not class_obj:
        raise HTTPException(404, detail="班级不存在")

    student_count = db.query(Student).filter(Student.class_id == exam.class_id).count()

    stats = {}
    for key in SUBJECT_KEYS:
        subject = Subject(key)
        score_vals = [
            s.score
            for s in db.query(Score.score)
            .filter(Score.exam_id == exam_id, Score.subject == subject)
            .all()
        ]

        if not score_vals:
            stats[key] = {
                "avg_score": 0, "max_score": 0, "min_score": 0,
                "pass_count": 0, "total_count": 0,
                "pass_rate": 0, "excellent_count": 0, "excellent_rate": 0,
                "distribution": {"under_60": 0, "range_60_69": 0, "range_70_79": 0,
                                 "range_80_89": 0, "range_90_100": 0},
            }
            continue

        avg = round(sum(score_vals) / len(score_vals), 1)
        max_s = max(score_vals)
        min_s = min(score_vals)
        total_count = len(score_vals)
        pass_count = sum(1 for v in score_vals if v >= 60)
        excellent_count = sum(1 for v in score_vals if v >= 90)

        stats[key] = {
            "avg_score": avg,
            "max_score": max_s,
            "min_score": min_s,
            "pass_count": pass_count,
            "total_count": total_count,
            "pass_rate": round(pass_count / total_count * 100, 1) if total_count else 0,
            "excellent_count": excellent_count,
            "excellent_rate": round(excellent_count / total_count * 100, 1) if total_count else 0,
            "distribution": {
                "under_60": sum(1 for v in score_vals if v < 60),
                "range_60_69": sum(1 for v in score_vals if 60 <= v < 70),
                "range_70_79": sum(1 for v in score_vals if 70 <= v < 80),
                "range_80_89": sum(1 for v in score_vals if 80 <= v < 90),
                "range_90_100": sum(1 for v in score_vals if v >= 90),
            },
        }

    # 权限过滤：非管理员且非班主任只能看到自己科目的统计
    if current_user.role != StaffRole.ADMIN:
        is_homeroom = class_obj.homeroom_teacher_id == current_user.id
        if not is_homeroom and current_user.subject:
            allowed = current_user.subject.value
            stats = {k: v for k, v in stats.items() if k == allowed}

    return ApiResponse(data={
        "exam_id": exam.id,
        "exam_name": exam.name,
        "class_id": exam.class_id,
        "class_name": class_obj.name,
        "student_count": student_count,
        "stats": stats,
    })
