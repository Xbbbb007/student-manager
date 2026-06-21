from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.staff import Staff
from ..models.student import Student
from ..models.class_model import Class
from ..models.enums import StaffRole
from ..schemas.user import ApiResponse
from ..core.security import decode_access_token
from ..services.auth import get_staff_by_id

router = APIRouter(prefix="/api/v1/classes", tags=["班级"])


def get_current_staff(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Staff:
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
        raise HTTPException(403, detail="仅教职工可查看")
    user = get_staff_by_id(db, int(payload.get("sub", 0)))
    if not user:
        raise HTTPException(404, detail="用户不存在")
    return user


@router.get("/", response_model=ApiResponse)
def list_classes(current_user: Staff = Depends(get_current_staff), db: Session = Depends(get_db)):
    if current_user.role != StaffRole.ADMIN:
        raise HTTPException(403, detail="仅管理员可查看")
    classes = db.query(Class).all()
    data = []
    for c in classes:
        teacher = db.query(Staff).filter(Staff.id == c.homeroom_teacher_id).first()
        student_count = db.query(Student).filter(Student.class_id == c.id).count()
        data.append({
            "id": c.id,
            "name": c.name,
            "section": c.section,
            "grade": c.grade,
            "homeroom_teacher": teacher.name if teacher else "",
            "homeroom_teacher_id": c.homeroom_teacher_id,
            "student_count": student_count
        })
    return ApiResponse(data=data)

