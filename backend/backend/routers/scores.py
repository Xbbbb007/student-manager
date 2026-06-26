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
from ..models.teacher_class import TeacherClass
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


@router.get("/subject-trend")
def get_subject_trend(
    class_id: int,
    subjects: Optional[str] = None,
    current_user: Staff = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """教师端：获取某班级某科目的历次考试均分趋势（本科目对比 / 跨科目对比）

    - subjects: 逗号分隔的科目 key，如 "chinese" 或 "chinese,math"
    - 科任老师只能查自己科目，班主任和管理员可查所有科目
    """
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(404, detail="班级不存在")

    # 解析科目列表
    requested = [s.strip() for s in subjects.split(",") if s.strip()] if subjects else ["chinese"]

    # 权限过滤
    allowed_subjects = set(SUBJECT_KEYS)
    if current_user.role != StaffRole.ADMIN:
        is_homeroom = class_obj.homeroom_teacher_id == current_user.id
        if not is_homeroom and current_user.subject:
            allowed_subjects = {current_user.subject.value}

    valid_subjects = [s for s in requested if s in allowed_subjects]
    if not valid_subjects:
        raise HTTPException(403, detail="无权查看所选科目的趋势")

    # 获取该班级的所有考试（按日期排序）
    exams = (
        db.query(Exam)
        .filter(Exam.class_id == class_id)
        .order_by(Exam.exam_date.asc(), Exam.id.asc())
        .all()
    )

    labels = []
    series: dict = {s: [] for s in valid_subjects}

    for exam in exams:
        labels.append(exam.name)
        for subj_key in valid_subjects:
            score_vals = [
                s.score for s in db.query(Score.score).filter(
                    Score.exam_id == exam.id,
                    Score.subject == Subject(subj_key),
                ).all()
            ]
            avg = round(sum(score_vals) / len(score_vals), 1) if score_vals else None
            series[subj_key].append(avg)

    return ApiResponse(data={
        "class_id": class_id,
        "class_name": class_obj.name,
        "labels": labels,
        "series": series,
        "subjects": {k: SUBJECT_MAP.get(k, k) for k in valid_subjects},
    })


# ═══════════════════════════════════════════════════════
# 教师端新 API — 班级筛选 + 仪表盘
# ═══════════════════════════════════════════════════════

@router.get("/teacher/classes")
def get_teacher_classes(
    current_user: Staff = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """获取教师所教班级列表（管理员返回全部）"""
    if current_user.role == StaffRole.ADMIN:
        classes = db.query(Class).order_by(Class.id).all()
        class_list = []
        for c in classes:
            student_count = db.query(Student).filter(Student.class_id == c.id).count()
            class_list.append({
                "id": c.id,
                "name": c.name,
                "section": c.section,
                "grade": c.grade,
                "student_count": student_count,
                "homeroom_teacher_id": c.homeroom_teacher_id,
            })
        return ApiResponse(data={
            "classes": class_list,
            "is_admin": True,
        })

    # 非管理员：查找自己是班主任的班级
    homeroom_classes = db.query(Class).filter(Class.homeroom_teacher_id == current_user.id).all()

    # 查找自己在 teacher_classes 里有授课的班级
    tcs = (
        db.query(Class)
        .join(TeacherClass, Class.id == TeacherClass.class_id)
        .filter(TeacherClass.teacher_id == current_user.id)
        .all()
    )

    # 去重并排序
    seen = set()
    my_classes = []
    for c in (homeroom_classes + tcs):
        if c.id not in seen:
            seen.add(c.id)
            my_classes.append(c)
    my_classes.sort(key=lambda x: x.id)

    class_list = []
    for c in my_classes:
        student_count = db.query(Student).filter(Student.class_id == c.id).count()
        class_list.append({
            "id": c.id,
            "name": c.name,
            "section": c.section,
            "grade": c.grade,
            "student_count": student_count,
            "homeroom_teacher_id": c.homeroom_teacher_id,
        })

    return ApiResponse(data={
        "classes": class_list,
        "is_admin": False,
    })


@router.get("/teacher/exams")
def get_teacher_exams(
    class_ids: str,
    current_user: Staff = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """获取多个班级的考试列表（按名称去重合并）

    class_ids: 逗号分隔的班级 ID，如 "1,2"
    """
    ids = [int(x.strip()) for x in class_ids.split(",") if x.strip().isdigit()]
    if not ids:
        return ApiResponse(data=[])

    exams = (
        db.query(Exam)
        .filter(Exam.class_id.in_(ids))
        .order_by(Exam.exam_date.asc(), Exam.id.asc())
        .all()
    )

    # 按 (name, exam_date) 分组
    grouped = {}
    for exam in exams:
        key = (exam.name, str(exam.exam_date) if exam.exam_date else "")
        if key not in grouped:
            grouped[key] = {
                "name": exam.name,
                "exam_date": str(exam.exam_date) if exam.exam_date else None,
                "exam_class_ids": [],
            }
        grouped[key]["exam_class_ids"].append({
            "exam_id": exam.id,
            "class_id": exam.class_id,
        })

    # 转为列表
    result = []
    for (name, _), group in grouped.items():
        result.append(group)

    return ApiResponse(data=result)


@router.get("/teacher-dashboard")
def get_teacher_dashboard(
    exam_ids: str,
    subject: str,
    current_user: Staff = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    """教师仪表盘：基础统计 + 前十名 + 波动TOP5 + 需关注学生

    exam_ids: 逗号分隔的考试 ID（单班传1个，总体传多个）
    subject:  科目 key
    """
    ids = [int(x.strip()) for x in exam_ids.split(",") if x.strip().isdigit()]
    if not ids:
        raise HTTPException(400, detail="缺少考试 ID")

    is_multi = len(ids) > 1

    # ── 收集所有成绩数据 ──────────────────────
    all_scores = (
        db.query(Score)
        .filter(Score.exam_id.in_(ids), Score.subject == Subject(subject))
        .all()
    )
    if not all_scores:
        return ApiResponse(data={
            "summary": None,
            "comparison": [],
            "top_students": [],
            "fluctuation": [],
            "needs_attention": [],
        })

    # ── 1. Summary 基础统计 ───────────────────
    score_vals = [s.score for s in all_scores]
    total_count = len(score_vals)
    summary = {
        "total_students": total_count,
        "avg_score": round(sum(score_vals) / total_count, 1),
        "max_score": max(score_vals),
        "min_score": min(score_vals),
        "pass_rate": round(sum(1 for v in score_vals if v >= 60) / total_count * 100, 1),
        "excellent_rate": round(sum(1 for v in score_vals if v >= 90) / total_count * 100, 1),
    }

    # ── 2. Comparison 班级对比（仅多考试时） ──
    comparison = []
    if is_multi:
        for eid in ids:
            exam = db.query(Exam).filter(Exam.id == eid).first()
            if not exam:
                continue
            class_obj = db.query(Class).filter(Class.id == exam.class_id).first()
            exam_scores = [s.score for s in all_scores if s.exam_id == eid]
            if not exam_scores:
                continue
            n = len(exam_scores)
            comparison.append({
                "exam_id": eid,
                "class_id": exam.class_id,
                "class_name": class_obj.name if class_obj else "",
                "total_students": n,
                "avg_score": round(sum(exam_scores) / n, 1),
                "max_score": max(exam_scores),
                "min_score": min(exam_scores),
                "pass_rate": round(sum(1 for v in exam_scores if v >= 60) / n * 100, 1),
                "excellent_rate": round(sum(1 for v in exam_scores if v >= 90) / n * 100, 1),
            })

    # ── 构建辅助映射 ──────────────────────────
    student_map = {
        s.id: s for s in db.query(Student)
        .filter(Student.id.in_([s.student_id for s in all_scores]))
        .all()
    }
    class_cache = {}
    def get_class_name(class_id):
        if class_id not in class_cache:
            c = db.query(Class).filter(Class.id == class_id).first()
            class_cache[class_id] = c.name if c else ""
        return class_cache[class_id]

    # ── 3. Top 10 前十名 ─────────────────────
    top_students = []
    for eid in ids:
        exam = db.query(Exam).filter(Exam.id == eid).first()
        if not exam:
            continue

        # 找上一次考试（同班级、同科目、日期更早）
        prev_exam = (
            db.query(Exam)
            .filter(Exam.class_id == exam.class_id,
                    Exam.exam_date < exam.exam_date)
            .order_by(Exam.exam_date.desc())
            .first()
        )

        current_scores = [s for s in all_scores if s.exam_id == eid]
        prev_scores = {}
        if prev_exam:
            for ps in db.query(Score).filter(
                Score.exam_id == prev_exam.id,
                Score.subject == Subject(subject),
            ).all():
                prev_scores[ps.student_id] = ps

        for s in current_scores:
            stu = student_map.get(s.student_id)
            if not stu:
                continue
            prev_s = prev_scores.get(s.student_id)
            top_students.append({
                "student_id": s.student_id,
                "student_name": stu.name,
                "username": stu.username,
                "score": s.score,
                "class_name": get_class_name(exam.class_id),
                "class_rank": s.class_rank,
                "rank_change": (prev_s.class_rank - s.class_rank) if prev_s and prev_s.class_rank else None,
                "score_change": round(s.score - prev_s.score, 1) if prev_s else None,
            })

    top_students.sort(key=lambda x: x["score"], reverse=True)
    top_students = top_students[:10]

    # ── 4. Fluctuation 波动最大 TOP5 ─────────
    fluctuation_map = {}
    for eid in ids:
        exam = db.query(Exam).filter(Exam.id == eid).first()
        if not exam:
            continue

        prev_exam = (
            db.query(Exam)
            .filter(Exam.class_id == exam.class_id,
                    Exam.exam_date < exam.exam_date)
            .order_by(Exam.exam_date.desc())
            .first()
        )
        if not prev_exam:
            continue

        current_scores = [s for s in all_scores if s.exam_id == eid]
        prev_scores = {}
        for ps in db.query(Score).filter(
            Score.exam_id == prev_exam.id,
            Score.subject == Subject(subject),
        ).all():
            prev_scores[ps.student_id] = ps

        for s in current_scores:
            prev_s = prev_scores.get(s.student_id)
            if not prev_s:
                continue
            change = round(s.score - prev_s.score, 1)
            abs_change = abs(change)
            # 同学生取最大波动
            if s.student_id not in fluctuation_map or abs_change > abs(fluctuation_map[s.student_id]["score_change"]):
                stu = student_map.get(s.student_id)
                if not stu:
                    continue
                fluctuation_map[s.student_id] = {
                    "student_id": s.student_id,
                    "student_name": stu.name,
                    "username": stu.username,
                    "score": s.score,
                    "prev_score": prev_s.score,
                    "score_change": change,
                    "class_rank": s.class_rank,
                    "prev_class_rank": prev_s.class_rank,
                    "rank_change": (prev_s.class_rank - s.class_rank) if (prev_s.class_rank and s.class_rank) else None,
                    "class_name": get_class_name(exam.class_id),
                }

    fluctuation = sorted(
        fluctuation_map.values(),
        key=lambda x: abs(x["score_change"]),
        reverse=True,
    )[:5]

    # ── 5. Needs Attention 需关注学生 ─────────
    # 连续两次分数下降的学生
    attention_map = {}
    for eid in ids:
        exam = db.query(Exam).filter(Exam.id == eid).first()
        if not exam:
            continue

        prev_exam = (
            db.query(Exam)
            .filter(Exam.class_id == exam.class_id,
                    Exam.exam_date < exam.exam_date)
            .order_by(Exam.exam_date.desc())
            .first()
        )
        if not prev_exam:
            continue

        prev_prev_exam = (
            db.query(Exam)
            .filter(Exam.class_id == exam.class_id,
                    Exam.exam_date < prev_exam.exam_date)
            .order_by(Exam.exam_date.desc())
            .first()
        )
        if not prev_prev_exam:
            continue

        current_scores = {s.student_id: s for s in all_scores if s.exam_id == eid}

        prev_scores = {}
        for ps in db.query(Score).filter(
            Score.exam_id == prev_exam.id,
            Score.subject == Subject(subject),
        ).all():
            prev_scores[ps.student_id] = ps

        prev_prev_scores = {}
        for pps in db.query(Score).filter(
            Score.exam_id == prev_prev_exam.id,
            Score.subject == Subject(subject),
        ).all():
            prev_prev_scores[pps.student_id] = pps

        for sid, curr_s in current_scores.items():
            prev_s = prev_scores.get(sid)
            prev_prev_s = prev_prev_scores.get(sid)
            if not prev_s or not prev_prev_s:
                continue

            # 连续两次下降
            if curr_s.score < prev_s.score and prev_s.score < prev_prev_s.score:
                stu = student_map.get(sid)
                if not stu:
                    continue
                attention_map[sid] = {
                    "student_id": sid,
                    "student_name": stu.name,
                    "username": stu.username,
                    "current_score": curr_s.score,
                    "prev_score": prev_s.score,
                    "prev_prev_score": prev_prev_s.score,
                    "trend": [
                        round(prev_s.score - prev_prev_s.score, 1),
                        round(curr_s.score - prev_s.score, 1),
                    ],
                    "class_name": get_class_name(exam.class_id),
                }

    needs_attention = list(attention_map.values())

    return ApiResponse(data={
        "summary": summary,
        "comparison": comparison,
        "top_students": top_students,
        "fluctuation": fluctuation,
        "needs_attention": needs_attention,
    })


@router.get("/export")
def export_scores_csv(
    exam_id: int,
    class_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_teacher),
):
    """教务/教师：导出班级成绩到 CSV"""
    import csv
    import io
    from fastapi.responses import StreamingResponse

    # 验证班级与考试是否存在
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(404, detail="班级不存在")
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(404, detail="考试不存在")

    # 查询该班级学生
    students = db.query(Student).filter(Student.class_id == class_id).all()
    if not students:
        raise HTTPException(400, detail="该班级暂无学生")

    output = io.StringIO()
    # 写入 UTF-8 BOM，防止 Excel 打开中文乱码
    output.write('\ufeff')
    writer = csv.writer(output)
    
    # 标题行
    headers = ["学号", "姓名", "班级", "语文", "数学", "英语", "科学", "道德与法治", "班级排名", "校排名"]
    writer.writerow(headers)
    
    for s in students:
        row = [s.username, s.name, class_obj.name]
        # 查询该学生此考试下的成绩
        scores = db.query(Score).filter(Score.student_id == s.id, Score.exam_id == exam_id).all()
        score_dict = {sc.subject.value: sc.score for sc in scores}
        
        # 排名
        class_rank = ""
        school_rank = ""
        if scores:
            class_rank = scores[0].class_rank or ""
            school_rank = scores[0].school_rank or ""
            
        row.append(score_dict.get("chinese", ""))
        row.append(score_dict.get("math", ""))
        row.append(score_dict.get("english", ""))
        row.append(score_dict.get("science", ""))
        row.append(score_dict.get("ethics", ""))
        row.append(class_rank)
        row.append(school_rank)
        
        writer.writerow(row)
        
    output.seek(0)
    filename = f"{class_obj.name}_{exam.name}_成绩汇总.csv"
    headers_response = {
        'Content-Disposition': f'attachment; filename="{filename.encode("utf-8").decode("latin-1")}"'
    }
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers=headers_response
    )

