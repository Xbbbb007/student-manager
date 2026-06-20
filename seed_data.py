import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from sqlalchemy import create_engine, text
from backend.database import Base
from backend.models.user import User, Class, UserRole, Gender, Subject
from backend.core.security import hash_password

engine = create_engine("mysql+pymysql://root:123456@localhost:3306/student_manager")

# 禁用外键检查，删表重建
with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    conn.execute(text("DROP TABLE IF EXISTS classes"))
    conn.execute(text("DROP TABLE IF EXISTS users"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    conn.commit()

Base.metadata.create_all(bind=engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
db = Session()

admin = User(username="admin", password_hash=hash_password("admin123"), password_plain="admin123", name="系统管理员", role=UserRole.ADMIN)
db.add(admin); db.flush()

teachers_data = [
    ("zhang_laoshi", "张老师", Subject.CHINESE, "male"),
    ("li_laoshi", "李老师", Subject.MATH, "female"),
    ("wang_laoshi", "王老师", Subject.ENGLISH, "female"),
]
teachers = []
for uname, name, subj, g in teachers_data:
    t = User(username=uname, password_hash=hash_password("123456"), password_plain="123456", name=name, role=UserRole.TEACHER, subject=subj, gender=Gender(g))
    db.add(t); db.flush(); teachers.append(t)

c1 = Class(name="三年级一班", grade="三年级", homeroom_teacher_id=teachers[1].id)
c2 = Class(name="三年级二班", grade="三年级", homeroom_teacher_id=teachers[1].id)
db.add(c1); db.add(c2); db.flush()

import random; random.seed(42)
male_names = ["刘子轩","陈浩宇","杨明远","赵天宇","黄梓涵","周子涵","吴俊杰","徐子豪","孙泽宇","马浩然","朱宇航","胡文博","林伟杰","何思远","高天阳","罗宇轩","梁嘉豪","宋致远","唐文昊","许泽楷","邓睿轩","冯俊哲","韩一鸣","曹博文","彭子骞","曾鹏飞","萧景行","程子墨","蔡子轩","魏浩然"]
female_names = ["陈雨桐","张语萱","王子涵","李若曦","赵梦瑶","刘诗琪","杨雅婷","黄思琪","周婉晴","吴思颖","徐欣怡","孙悦然","马可欣","朱芷晴","胡梓涵","林静怡","何思琪","高梓萱","罗雨欣","梁芷柔","宋佳琪","唐雅静","许梦洁","邓思涵","冯梓萌","韩雨桐","曹可欣","彭语嫣","曾芷晴","萧雅文"]
random.shuffle(male_names); random.shuffle(female_names)

for i in range(15):
    db.add(User(username=f"s{i+1:02d}", password_hash=hash_password("123456"), password_plain="123456", name=male_names[i], role=UserRole.STUDENT, gender=Gender.MALE, class_id=c1.id))
for i in range(15):
    db.add(User(username=f"s{i+16:02d}", password_hash=hash_password("123456"), password_plain="123456", name=female_names[i], role=UserRole.STUDENT, gender=Gender.FEMALE, class_id=c1.id))
for i in range(15, 30):
    db.add(User(username=f"s{i+31:02d}", password_hash=hash_password("123456"), password_plain="123456", name=male_names[i], role=UserRole.STUDENT, gender=Gender.MALE, class_id=c2.id))
for i in range(15, 30):
    db.add(User(username=f"s{i+31:02d}", password_hash=hash_password("123456"), password_plain="123456", name=female_names[i], role=UserRole.STUDENT, gender=Gender.FEMALE, class_id=c2.id))

db.commit(); db.close()
print("OK - Seed data created!")
