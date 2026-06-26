"""填充 teacher_classes 关联表"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import Staff, Class, TeacherClass

engine = create_engine("mysql+pymysql://root:3274594297@localhost:3306/student_manager")

# 确保表已创建
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
db = Session()

# 清空旧数据
db.query(TeacherClass).delete()
db.commit()

# 查找所有教师和班级
teachers = {s.username: s for s in db.query(Staff).all()}
classes = {c.name: c for c in db.query(Class).all()}

# 定义映射关系: (教师username, 班级name, subject)
assignments = []

# ─── 小学部三年级（一班 id=1, 二班 id=2）───────────────
for uname, subj in [
    ("zhang_laoshi", "chinese"), ("li_laoshi", "math"), ("wang_laoshi", "english"),
    ("zhang_sci", "science"),    ("zhang_eth", "ethics"),
]:
    if uname in teachers:
        for cname in ["小学部三年级一班", "小学部三年级二班"]:
            if cname in classes:
                assignments.append((uname, cname, subj))

# ─── 小学部四年级（一班 id=3, 二班 id=4）───────────────
for uname, subj in [
    ("zhao_laoshi", "chinese"), ("sun_laoshi", "math"), ("qian_laoshi", "english"),
    ("zhao_sci", "science"),    ("zhao_eth", "ethics"),
]:
    if uname in teachers:
        for cname in ["小学部四年级一班", "小学部四年级二班"]:
            if cname in classes:
                assignments.append((uname, cname, subj))

# ─── 小学部五年级 ──────────────────────────────────────
for uname, subj in [
    ("wu_chi", "chinese"), ("wu_math", "math"), ("wu_eng", "english"),
    ("wu_sci", "science"),    ("wu_eth", "ethics"),
]:
    if uname in teachers:
        for cname in ["小学部五年级一班", "小学部五年级二班"]:
            if cname in classes:
                assignments.append((uname, cname, subj))

# ─── 小学部六年级 ──────────────────────────────────────
for uname, subj in [
    ("zheng_chi", "chinese"), ("zheng_math", "math"), ("zheng_eng", "english"),
    ("zheng_sci", "science"),    ("zheng_eth", "ethics"),
]:
    if uname in teachers:
        for cname in ["小学部六年级一班", "小学部六年级二班"]:
            if cname in classes:
                assignments.append((uname, cname, subj))

# ─── 初中部一年级 ─────────────────────────────────────
for uname, subj in [
    ("chen_laoshi", "chinese"), ("yang_laoshi", "math"), ("liu_laoshi", "english"),
]:
    if uname in teachers:
        for cname in ["初中部一年级一班", "初中部一年级二班"]:
            if cname in classes:
                assignments.append((uname, cname, subj))

# ─── 初中部二年级 ─────────────────────────────────────
for uname, subj in [
    ("huang_laoshi", "chinese"), ("zhou_laoshi", "math"), ("wu_laoshi", "english"),
]:
    if uname in teachers:
        for cname in ["初中部二年级一班", "初中部二年级二班"]:
            if cname in classes:
                assignments.append((uname, cname, subj))

# 批量插入
count = 0
for uname, cname, subj in assignments:
    t = teachers[uname]
    c = classes[cname]
    db.add(TeacherClass(teacher_id=t.id, class_id=c.id, subject=subj))
    count += 1

db.commit()
db.close()

print(f"✅ teacher_classes 填充完毕，共 {count} 条记录")
for uname, cname, subj in assignments:
    print(f"  {uname:15s} → {cname:20s} ({subj})")
