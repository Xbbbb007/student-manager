from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional, List

from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.user import ApiResponse, UserInfo
from ..services.auth import create_user, get_user_by_id
from ..core.security import decode_access_token

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(401, detail="缺少认证信息")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, detail="Token 格式错误")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(401, detail="Token 无效")
    user_id = int(payload.get("sub", 0))
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, detail="用户不存在")
    return user


class UserCreateRequest:
    username: str
    password: str
    name: str
    role: str


@router.get("/", response_model=ApiResponse)
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(403, detail="仅管理员可查看用户列表")
    users = db.query(User).all()
    data = [
        {
            "id": u.id,
            "username": u.username,
            "name": u.name,
            "role": u.role.value,
            "password_plain": u.password_plain or ""
        }
        for u in users
    ]
    return ApiResponse(data=data)


@router.post("/", response_model=ApiResponse)
def create_user_api(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(403, detail="仅管理员可创建用户")
    username = body.get("username")
    password = body.get("password")
    name = body.get("name")
    role = body.get("role", "student")
    if not all([username, password, name]):
        raise HTTPException(400, detail="缺少必填字段")
    if role not in [e.value for e in UserRole]:
        raise HTTPException(400, detail="无效角色")
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(400, detail="用户名已存在")
    user = create_user(db, username, password, name, role)
    return ApiResponse(data={
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "role": user.role.value,
        "password_plain": user.password_plain or ""
    })


@router.delete("/{user_id}", response_model=ApiResponse)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(403, detail="仅管理员可删除用户")
    if current_user.id == user_id:
        raise HTTPException(400, detail="不能删除自己")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return ApiResponse(message="删除成功")


@router.put("/{user_id}", response_model=ApiResponse)
def update_user(
    user_id: int,
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(403, detail="仅管理员可修改用户")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="用户不存在")
    if "name" in body:
        user.name = body["name"]
    if "password" in body and body["password"]:
        from ..core.security import hash_password
        user.password_hash = hash_password(body["password"])
        user.password_plain = body["password"]
    db.commit()
    db.refresh(user)
    return ApiResponse(data={
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "role": user.role.value,
        "password_plain": user.password_plain or ""
    })
