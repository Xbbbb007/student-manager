# 智慧学生管理系统

> 面向中小学教育场景的智慧学生管理系统，覆盖学生、教师、管理员三种角色，提供从日常教务到学情分析的全流程数字化解决方案。

> 📋 **开发计划及各模块详细设计请看 [`PLAN.md`](PLAN.md)**

## 技术栈

| 层级 | 技术方案 |
|------|---------|
| **前端** | Vue 3 + TypeScript + Element Plus + Pinia + Vue Router + Chart.js + GSAP |
| **后端** | Python FastAPI + SQLAlchemy + JWT + bcrypt + PyMySQL |
| **数据库** | MySQL（root/123456，数据库 student_manager） |
| **动画** | GSAP（导航滑动指示条、页面平滑过渡、弹窗动画） |
| **图表** | Chart.js（成绩趋势柱状图+折线图、学科能力雷达图、考勤趋势线图、作业提交率柱状图） |
| **AI** | LangChain + DeepSeek API（待接入） |

## 项目结构

```
D:\Dev\demo\
├── frontend/              # Vue 3 前端项目
│   └── src/
│       ├── api/           # API 请求封装（auth, users, classes, scores, homework, teaching, etc.）
│       ├── router/        # 路由 + 角色权限登录守卫
│       ├── stores/        # Pinia 用户/状态管理
│       ├── styles/        # 东方青蓝设计系统 (SCSS Token)
│       └── views/
│           ├── student/   # 学生端（学习主页、课表、生活点滴、个人信息、成绩诊断、作业、错题本、请假）
│           ├── teacher/   # 教师端（教学主页、成绩录入、课表查看、作业发布与批改、出卷组卷、资源库）
│           └── admin/     # 管理端（用户账号管理、教务排课、全校考勤/作业大屏、成绩导出）
├── backend/               # FastAPI 后端项目
│   └── backend/
│       ├── core/          # 全局配置 + 安全认证 (JWT & bcrypt)
│       ├── models/        # SQLAlchemy 数据模型 (17张表)
│       ├── routers/       # API 路由控制 (auth, users, classes, scores, exams, schedules, homework, teaching, mistakes, attendance)
│       ├── schemas/       # Pydantic 校验模型
│       └── services/      # 业务逻辑服务层
├── docs/                  # 设计系统与规范文档
├── PLAN.md                # 统一开发计划（最新状态）
├── HANDOFF.md             # 项目交接文档（最新状态）
├── 进度.md                 # 进度追踪（最新状态）
├── student_manager.sql    # 完整的本地 MySQL 备份（包含17张表的结构及种子数据）
└── seed_data.py           # 数据库基础种子填充脚本（还有 seed_teaching.py, seed_homework.py 等）
```

## 数据库结构（17张表）

| 表名 | 说明 | 主要字段 |
|------|------|---------|
| `staff` | 教职工表（管理员+教师） | id, username, password_hash, password_plain, name, role(teacher/admin), gender, subject |
| `students` | 学生表 | id, username(学号), password_hash, password_plain, name, gender, class_id |
| `classes` | 班级表 | id, name, section(小学部/初中部), grade, homeroom_teacher_id |
| `exams` | 成绩考试表 | id, name, class_id, exam_date, created_at |
| `scores` | 学生成绩表 | id, student_id, exam_id, subject, score, class_rank, school_rank |
| `schedules` | 课表数据表 | id, class_id, day_of_week, period, subject, teacher_id |
| `teacher_classes` | 教师与班级科目关联表 | id, teacher_id, class_id, subject |
| `homeworks` | 作业布置信息表 | id, title, description, subject, class_id, teacher_id, due_date, created_at |
| `homework_submissions` | 学生作业提交及教师批改表 | id, homework_id, student_id, content, submitted_at, grade, feedback, status |
| `exam_schedules` | 考试安排日程表 | id, name, class_id, subject, exam_date, start_time, end_time, location, status |
| `test_submissions` | 在线测验提交记录表 | id, schedule_id, student_id, score, answers, submitted_at, status |
| `mistakes` | 学生错题本记录表 | id, student_id, subject, exam_id, test_id, question_desc, my_answer, correct_answer, is_mastered, created_at |
| `attendance` | 考勤打卡明细表 | id, student_id, class_id, date, period, status, reason |
| `leave_requests` | 学生请假申请审批表 | id, student_id, start_date, end_date, reason, status, approved_by, feedback |
| `questions` | 教学资源库-题目表 | id, subject, question_type, question_desc, difficulty, answer, explanation, created_by |
| `exam_papers` | 教学资源库-试卷表 | id, title, subject, difficulty, questions(JSON), created_by, created_at |
| `resources` | 教学资源库-课件资料表 | id, title, subject, grade, file_name, file_path, upload_by, created_at |

**学号规则**：`SS GG CC NN`（学部2位 + 年级2位 + 班级2位 + 序号2位）
* `01` 代表小学部，`02` 代表初中部
* 示例：`01050105` = 小学部五年级一班第5号学生

## 快速开始

### 后端服务启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动 FastAPI 开发服务器
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端服务启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动 Vite 开发服务器
npm run dev
```

## 测试账号

| 角色 | 账号 | 密码 | 对应说明 |
|------|------|------|---------|
| 管理员 | `admin` | `admin123` | 系统全局管理权限 |
| 三年级语文老师（班主任） | `zhang_laoshi` | `123456` | 班主任权限，可管理三1班各科成绩与考勤审批 |
| 三年级科学老师（科任） | `zhang_sci` | `123456` | 科任教师，可管理所教班级的科学科目成绩及出卷 |
| 学生（三年级一班） | `01030106` | `123456` | 访问学生端（学习/课表/生活/请假/成绩趋势） |
| 学生（五年级一班） | `01050101` | `123456` | 访问学生端 |

## 🔗 GitHub 仓库

- https://github.com/Xbbbb007/student-manager
