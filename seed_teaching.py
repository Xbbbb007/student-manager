import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import Staff
from backend.models.teaching import Question, ExamPaper, Resource

engine = create_engine("mysql+pymysql://root:3274594297@localhost:3306/student_manager")
print("Creating teaching tables if they don't exist...")
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
db = Session()

# Check if already seeded
if db.query(Question).count() > 0:
    print("Teaching questions already seeded.")
    sys.exit(0)

# Get a staff user for creation reference
teacher = db.query(Staff).filter(Staff.role == "teacher").first()
teacher_id = teacher.id if teacher else 1

print(f"Seeding questions and resources with teacher ID: {teacher_id}")

# 1. Seed Questions
questions = [
    # Chinese
    Question(
        subject="chinese",
        question_type="single",
        question_desc="《静夜思》的作者是谁？\nA. 李白\nB. 杜甫\nC. 白居易\nD. 王维",
        difficulty="easy",
        answer="A",
        explanation="《静夜思》是唐代诗人李白的经典作品。",
        created_by=teacher_id
    ),
    Question(
        subject="chinese",
        question_type="blank",
        question_desc="根据诗句填空：欲穷千里目，___________。",
        difficulty="medium",
        answer="更上一层楼",
        explanation="出自王之涣的《登鹳雀楼》。",
        created_by=teacher_id
    ),
    Question(
        subject="chinese",
        question_type="essay",
        question_desc="请简要分析《春晓》中‘春眠不觉晓，处处闻啼鸟’所描绘的意境。",
        difficulty="hard",
        answer="描绘了春天清晨生机勃勃、自然和谐的景象，表现了作者对春天的喜爱之情。",
        explanation="通过听觉和视觉，生动传神地表达春天的气息。",
        created_by=teacher_id
    ),
    # Math
    Question(
        subject="math",
        question_type="single",
        question_desc="若 2x + 5 = 15，则 x 的值是多少？\nA. 5\nB. 10\nC. 15\nD. 20",
        difficulty="easy",
        answer="A",
        explanation="2x = 10 -> x = 5。",
        created_by=teacher_id
    ),
    Question(
        subject="math",
        question_type="blank",
        question_desc="直角三角形中两直角边长分别为3和4，则斜边长度为______。",
        difficulty="medium",
        answer="5",
        explanation="根据勾股定理，3的平方 + 4的平方 = 5的平方。",
        created_by=teacher_id
    ),
    Question(
        subject="math",
        question_type="essay",
        question_desc="请证明：任何偶数都可以表示为两个奇数之和。",
        difficulty="hard",
        answer="设偶数为 2n (n为正整数)，则可以写为 (2n-1) + 1，其中 2n-1 和 1 均为奇数，证毕。",
        explanation="基本代数性质证明。",
        created_by=teacher_id
    ),
    # English
    Question(
        subject="english",
        question_type="single",
        question_desc="What is the plural form of 'child'?\nA. childs\nB. children\nC. childrens\nD. childes",
        difficulty="easy",
        answer="B",
        explanation="'child' 的复数形式是规则变化的不规则形式 'children'。",
        created_by=teacher_id
    ),
    # Science
    Question(
        subject="science",
        question_type="single",
        question_desc="地球绕太阳公转一周的时间大约是多少？\nA. 24小时\nB. 一年 (365天)\nC. 一个月\nD. 一万年",
        difficulty="easy",
        answer="B",
        explanation="地球公转周期为一年，自转周期为一天。",
        created_by=teacher_id
    ),
    # Ethics
    Question(
        subject="ethics",
        question_type="single",
        question_desc="在人行横道过马路时，红灯亮起应该怎么做？\nA. 快速跑过去\nB. 停下等待绿灯\nC. 直接走过去\nD. 跟着大家一起走",
        difficulty="easy",
        answer="B",
        explanation="红灯停，绿灯行是交通基本常识与法律规章。",
        created_by=teacher_id
    ),
]

db.add_all(questions)
db.commit()

# Query back the added question IDs to associate them in mock papers
q_ids = [q.id for q in db.query(Question).all()]

# 2. Seed ExamPapers
papers = [
    ExamPaper(
        title="三年级上学期语文月考试卷（模版）",
        subject="chinese",
        difficulty="easy",
        questions=q_ids[:3],
        created_by=teacher_id
    ),
    ExamPaper(
        title="三年级数学综合测试卷",
        subject="math",
        difficulty="medium",
        questions=q_ids[3:6],
        created_by=teacher_id
    ),
]
db.add_all(papers)

# 3. Seed Resources
resources = [
    Resource(
        title="三年级上册语文《静夜思》多媒体公开课课件",
        subject="chinese",
        grade="三年级",
        file_name="jingyesi_ppt.pdf",
        file_path="/static/uploads/jingyesi_ppt.pdf",
        upload_by=teacher_id
    ),
    Resource(
        title="小学三年级数学《勾股定理及其应用》精编教案",
        subject="math",
        grade="三年级",
        file_name="gougu_dingli_doc.pdf",
        file_path="/static/uploads/gougu_dingli_doc.pdf",
        upload_by=teacher_id
    ),
    Resource(
        title="科学探究实验安全教育课件",
        subject="science",
        grade="四年级",
        file_name="science_safety.pdf",
        file_path="/static/uploads/science_safety.pdf",
        upload_by=teacher_id
    ),
]
db.add_all(resources)

db.commit()
print("Successfully seeded questions, exam papers, and teaching resources data!")
