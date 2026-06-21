"""种子数据脚本 — 按新规则创建学号"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from sqlalchemy import create_engine, text
from backend.database import Base
from backend.models import Staff, Student, Class, StaffRole, Gender, Subject
from backend.core.security import hash_password

engine = create_engine("mysql+pymysql://root:123456@localhost:3306/student_manager")

with engine.connect() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    conn.execute(text("DROP TABLE IF EXISTS classes"))
    conn.execute(text("DROP TABLE IF EXISTS students"))
    conn.execute(text("DROP TABLE IF EXISTS staff"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    conn.commit()

Base.metadata.create_all(bind=engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
db = Session()

import random; random.seed(42)

# ─── 管理员 ────────────────────────────────

admin = Staff(username="admin", password_hash=hash_password("admin123"),
              password_plain="admin123", name="系统管理员", role=StaffRole.ADMIN)
db.add(admin); db.flush()

# ─── 教职工 ────────────────────────────────

staff_list = []

# 小学部教师（三年级）
for uname, name, subj, g in [
    ("zhang_laoshi", "张老师", Subject.CHINESE, Gender.MALE),
    ("li_laoshi",   "李老师", Subject.MATH,   Gender.FEMALE),
    ("wang_laoshi", "王老师", Subject.ENGLISH, Gender.FEMALE),
]:
    t = Staff(username=uname, password_hash=hash_password("123456"), password_plain="123456",
              name=name, role=StaffRole.TEACHER, subject=subj, gender=g)
    db.add(t); db.flush(); staff_list.append(t)

# 小学部教师（四年级）
for uname, name, subj, g in [
    ("zhao_laoshi", "赵老师", Subject.CHINESE, Gender.FEMALE),
    ("sun_laoshi",  "孙老师", Subject.MATH,   Gender.MALE),
    ("qian_laoshi", "钱老师", Subject.ENGLISH, Gender.MALE),
]:
    t = Staff(username=uname, password_hash=hash_password("123456"), password_plain="123456",
              name=name, role=StaffRole.TEACHER, subject=subj, gender=g)
    db.add(t); db.flush(); staff_list.append(t)

# 初中部教师（一年级）
for uname, name, subj, g in [
    ("chen_laoshi", "陈老师", Subject.CHINESE, Gender.FEMALE),
    ("yang_laoshi", "杨老师", Subject.MATH,   Gender.MALE),
    ("liu_laoshi",  "刘老师", Subject.ENGLISH, Gender.FEMALE),
]:
    t = Staff(username=uname, password_hash=hash_password("123456"), password_plain="123456",
              name=name, role=StaffRole.TEACHER, subject=subj, gender=g)
    db.add(t); db.flush(); staff_list.append(t)

# 初中部教师（二年级）
for uname, name, subj, g in [
    ("huang_laoshi","黄老师", Subject.CHINESE, Gender.MALE),
    ("zhou_laoshi", "周老师", Subject.MATH,   Gender.FEMALE),
    ("wu_laoshi",   "吴老师", Subject.ENGLISH, Gender.MALE),
]:
    t = Staff(username=uname, password_hash=hash_password("123456"), password_plain="123456",
              name=name, role=StaffRole.TEACHER, subject=subj, gender=g)
    db.add(t); db.flush(); staff_list.append(t)

# ─── 班级 ──────────────────────────────────
# 格式: section(学段) + grade(年级)
# 小学部三年级 一班/二班
c_primary_g3_01 = Class(name="小学部三年级一班", section="小学部", grade="三年级", homeroom_teacher_id=staff_list[1].id)
c_primary_g3_02 = Class(name="小学部三年级二班", section="小学部", grade="三年级", homeroom_teacher_id=staff_list[1].id)
# 小学部四年级 一班/二班
c_primary_g4_01 = Class(name="小学部四年级一班", section="小学部", grade="四年级", homeroom_teacher_id=staff_list[4].id)
c_primary_g4_02 = Class(name="小学部四年级二班", section="小学部", grade="四年级", homeroom_teacher_id=staff_list[4].id)
# 初中部一年级 一班/二班
c_middle_g1_01 = Class(name="初中部一年级一班", section="初中部", grade="一年级", homeroom_teacher_id=staff_list[7].id)
c_middle_g1_02 = Class(name="初中部一年级二班", section="初中部", grade="一年级", homeroom_teacher_id=staff_list[7].id)
# 初中部二年级 一班/二班
c_middle_g2_01 = Class(name="初中部二年级一班", section="初中部", grade="二年级", homeroom_teacher_id=staff_list[10].id)
c_middle_g2_02 = Class(name="初中部二年级二班", section="初中部", grade="二年级", homeroom_teacher_id=staff_list[10].id)

classes = [
    c_primary_g3_01, c_primary_g3_02,
    c_primary_g4_01, c_primary_g4_02,
    c_middle_g1_01, c_middle_g1_02,
    c_middle_g2_01, c_middle_g2_02,
]
for c in classes:
    db.add(c)
db.flush()

# ─── 班级 → 学号前缀映射 ──────────────────
# {class_obj: (section_code, grade_code, class_code)}
CLASS_CODE = {
    c_primary_g3_01.id: ("01", "03", "01"),
    c_primary_g3_02.id: ("01", "03", "02"),
    c_primary_g4_01.id: ("01", "04", "01"),
    c_primary_g4_02.id: ("01", "04", "02"),
    c_middle_g1_01.id:  ("02", "01", "01"),
    c_middle_g1_02.id:  ("02", "01", "02"),
    c_middle_g2_01.id:  ("02", "02", "01"),
    c_middle_g2_02.id:  ("02", "02", "02"),
}

# 各班级学生名单
MALE_NAMES = [
    "刘子轩","陈浩宇","杨明远","赵天宇","黄梓涵","周子涵","吴俊杰","徐子豪","孙泽宇","马浩然",
    "朱宇航","胡文博","林伟杰","何思远","高天阳","罗宇轩","梁嘉豪","宋致远","唐文昊","许泽楷",
    "邓睿轩","冯俊哲","韩一鸣","曹博文","彭子骞","曾鹏飞","萧景行","程子墨","蔡子轩","魏浩然",
    "郑天翔","谢宇轩","谭浩铭","蒋睿泽","沈子骞","韩景行","贾博超","夏宇晨","苏睿渊","范一鸣",
    "方泽楷","石致远","姚天阳","廖文昊","熊子轩","金明远","余浩宇","潘梓涵","龚子豪","陆泽宇",
    "孔浩然","崔俊杰","白子涵","武文博","史思远","贺天宇","顾宇航","乔伟杰","汪子豪","邱泽宇",
    "叶昊天","龙泽宇","侯俊豪","邵宇晨","孟浩宇","段天宇","雷梓涵","乔景行","谭泽楷","汤文昊",
    "尹博文","汪宇轩","田子骞","任俊杰","姜浩铭","范致远","方思远","石天阳","邹伟杰","苏睿渊",
    "潘泽宇","葛浩然","范梓涵","彭子豪","曾浩宇","蔡梓涵","魏俊哲","夏宇晨","肖博超","戴景行",
    "贾浩宇","沈泽宇","蒋子涵","余天阳","廖泽楷","熊宇轩","金浩铭","余致远","罗俊杰","梁宇晨",
    "宋天宇","唐文博","韩子骞","曹景行","邓泽楷","冯文昊","韩宇轩","曹天阳","彭思远","曾伟杰",
    "程俊豪","蔡浩铭","魏宇晨","胡博超","林景行","何泽楷","高文昊","罗天阳","梁思远","宋伟杰",
]
FEMALE_NAMES = [
    "陈雨桐","张语萱","王子涵","李若曦","赵梦瑶","刘诗琪","杨雅婷","黄思琪","周婉晴","吴思颖",
    "徐欣怡","孙悦然","马可欣","朱芷晴","胡梓涵","林静怡","何思琪","高梓萱","罗雨欣","梁芷柔",
    "宋佳琪","唐雅静","许梦洁","邓思涵","冯梓萌","韩雨桐","曹可欣","彭语嫣","曾芷晴","萧雅文",
    "苏雨桐","范语萱","沈梓涵","韩若曦","贾梦瑶","夏诗琪","廖雅婷","熊思琪","金婉晴","余思颖",
    "潘欣怡","龚悦然","陆可欣","孔芷晴","白梓涵","崔静怡","武思琪","史梓萱","贺雨欣","顾芷柔",
    "乔佳琪","汪雅静","邱梦洁","苏思涵","范梓萌","沈雨桐","韩可欣","贾语嫣","夏芷晴","廖雅文",
    "叶雨彤","龙语萱","侯梓萱","邵雨桐","孟可欣","段芷晴","雷梓萌","乔语嫣","谭思涵","汤梓萌",
    "尹雨桐","汪可欣","田芷晴","任梓涵","姜若曦","范诗琪","方雅婷","石思琪","邹婉晴","苏思颖",
    "潘欣怡","葛悦然","范可欣","彭芷晴","曾梓涵","蔡静怡","魏思琪","夏梓萱","肖雨欣","戴芷柔",
    "贾佳琪","沈雅静","蒋梦洁","余思涵","廖梓萌","熊雨桐","金可欣","余语嫣","罗芷晴","梁雅文",
    "宋雨彤","唐语萱","韩梓萱","曹雨桐","邓可欣","冯芷晴","韩梓萌","曹语嫣","彭思涵","曾梓萌",
    "程雨欣","蔡芷柔","魏佳琪","胡雅静","林梦洁","何思涵","高梓萌","罗雨桐","梁可欣","宋语嫣",
]

random.shuffle(MALE_NAMES)
random.shuffle(FEMALE_NAMES)

name_pool_male = list(MALE_NAMES)
name_pool_female = list(FEMALE_NAMES)

total_students = 0

for c in classes:
    sc, gc, cc = CLASS_CODE[c.id]
    # 每班男生15人、女生15人 = 30人
    for seq in range(1, 16):
        username = f"{sc}{gc}{cc}{seq:02d}"
        name = name_pool_male.pop()
        db.add(Student(username=username, password_hash=hash_password("123456"),
                        password_plain="123456", name=name, gender=Gender.MALE, class_id=c.id))
        total_students += 1
    for seq in range(16, 31):
        username = f"{sc}{gc}{cc}{seq:02d}"
        name = name_pool_female.pop()
        db.add(Student(username=username, password_hash=hash_password("123456"),
                        password_plain="123456", name=name, gender=Gender.FEMALE, class_id=c.id))
        total_students += 1

db.commit()
db.close()

print("=" * 60)
print("种子数据生成完毕！")
print(f"  管理员: 1人 (admin / admin123)")
print(f"  教职工: {len(staff_list)}人 (均 / 123456)")
print(f"  班级数: {len(classes)}个")
print(f"  学生数: {total_students}人 (均 / 123456)")
print()
print("班级列表:")
for c in classes:
    sc, gc, cc = CLASS_CODE[c.id]
    print(f"  {c.name:20s} → 学号前缀 {sc}{gc}{cc}XX")
print()
print("学号示例:")
print("  初中部一年级二班 第20人 → 02010120")
print("  小学部三年级一班 第05人 → 01030105")
print("  小学部四年级二班 第18人 → 01040218")
print("=" * 60)
