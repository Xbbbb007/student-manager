"""考试管理路由"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from ..database import get_db
from ..models.exam import Exam
from ..models.class_model import Class
from ..models.staff import Staff
from ..models.enums import StaffRole
from ..schemas.exam import ExamCreate, ExamResponse
from ..schemas.user import ApiResponse
from ..services.auth import get_staff_by_id
from ..core.security import decode_access_token

router = APIRouter(prefix="/api/v1/exams", tags=["考试管理"])


def get_current_staff(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> Staff:
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


@router.get("/")
def list_exams(
    class_id: Optional[int] = None,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """获取考试列表，可按班级过滤"""
    query = db.query(Exam)
    if class_id:
        query = query.filter(Exam.class_id == class_id)
    exams = query.order_by(Exam.exam_date.asc(), Exam.id.asc()).all()

    data = []
    for exam in exams:
        class_obj = db.query(Class).filter(Class.id == exam.class_id).first()
        data.append({
            "id": exam.id,
            "name": exam.name,
            "class_id": exam.class_id,
            "class_name": class_obj.name if class_obj else "",
            "exam_date": str(exam.exam_date) if exam.exam_date else None,
            "created_at": str(exam.created_at) if exam.created_at else None,
        })

    return ApiResponse(data=data)


@router.post("/")
def create_exam(
    body: ExamCreate,
    current_user: Staff = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """创建新考试（仅管理员或教师）"""
    if current_user.role not in [StaffRole.ADMIN, StaffRole.TEACHER]:
        raise HTTPException(403, detail="仅教师和管理员可创建考试")

    class_obj = db.query(Class).filter(Class.id == body.class_id).first()
    if not class_obj:
        raise HTTPException(404, detail="班级不存在")

    exam = Exam(
        name=body.name,
        class_id=body.class_id,
        exam_date=body.exam_date,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    return ApiResponse(data={
        "id": exam.id,
        "name": exam.name,
        "class_id": exam.class_id,
        "exam_date": str(exam.exam_date) if exam.exam_date else None,
    })
