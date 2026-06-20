"""
FastAPI 主入口 - 智慧学生管理系统后端
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .core.config import settings
from .database import engine, Base
from .routers.auth import router as auth_router
from .routers.users import router as users_router
from .services.auth import init_admin
from .database import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN password_plain VARCHAR(128) DEFAULT ''"))
            conn.commit()
    except Exception:
        pass
    db = SessionLocal()
    try:
        init_admin(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "version": settings.APP_VERSION}
