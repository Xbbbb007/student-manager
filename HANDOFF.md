# 🤝 项目交接文档

> 供下一位接手 Agent 快速了解上下文，避免从头翻代码。
>
> 📋 **详细功能计划请看 [PLAN.md](PLAN.md)**

---

## 1️⃣ 当前状态

| 项目 | 值 |
|------|----|
| 已完成阶段 | **0~4.7**（环境搭建 / 设计系统 / 导航栏 / 认证与验证码 / 用户管理 / 成绩 / 课表 / 作业 / 排考 / 错题本 / 考勤与请假 / 教学增强与资源 / 智能排课与数据大屏） |
| 下一阶段 | **5.0** — AI 智能分析 (DeepSeek API 接入及深度应用) |
| 当前分支 | `main` |
| 数据库 | MySQL `student_manager`（包含 17 张表） |

---

## 2️⃣ 数据库表结构 (17张表)

### 教职工及学生主体
* **`staff`**：教职工表。角色分为 `admin` / `teacher`。若为教师，则包含 `subject` (任教科目)。
* **`students`**：学生表。包含 `username` (8位学号)、`class_id` 外键。
* **`classes`**：班级表。字段包括 `name` (如"小学部三年级一班")、`section` (小学部/初中部)、`grade`、`homeroom_teacher_id` (班主任ID)。
* **`teacher_classes`**：教师-班级-科目关联表。用于控制科任老师对特定班级特定科目的管理权限。

### 教学管理与成绩
* **`exams`**：考试发布表。包含考试名称、对应班级、考试日期。
* **`scores`**：成绩明细表。包含得分、排名等（`class_rank` 班内排名, `school_rank` 年级排名，保存成绩时通过 DENSE_RANK 自动重算）。
* **`schedules`**：周课表项目表。按 `class_id` + `day_of_week` (1-5) + `period` (1-8) 唯一约束存储科目与任课老师。

### 作业模块
* **`homeworks`**：作业布置表。包含标题、要求描述、截止日期。
* **`homework_submissions`**：学生作业提交及教师批改表。包括内容、得分 (`grade`)、批改评语 (`feedback`) 以及状态 (`submitted`/`graded`)。

### 考勤与请假模块
* **`attendance`**：课堂考勤明细表。按日按节 (`period` 1-8) 记录学生出勤状态：`present`, `tardy`, `absent`, `leave`。
* **`leave_requests`**：请假申请流转表。支持学生端发起，包含起止日期、原因，由教师进行状态审批 (`pending`/`approved`/`rejected`)，审批同意后自动同步考勤表。

### 排考与在线测试
* **`exam_schedules`**：排考日程表。包含科目、考试日期、时间段、考场位置及状态。
* **`test_submissions`**：在线小测提交记录表。记录学生在线测验的得分及答案详情。

### 错题本模块
* **`mistakes`**：错题本记录表。学生自主录入题目描述、我的解答、正确解析并标记是否掌握 (`is_mastered`)。

### 资源库与题库（教学增强）
* **`questions`**：公共/个人题库表。存储题干、类型 (单选/多选/填空/简答)、难度 (`easy`/`medium`/`hard`) 及答案解析。
* **`exam_papers`**：生成的试卷表。以 JSON 数组形式存储题目 ID 关联。
* **`resources`**：课件及教学资源表。记录文件名、物理存储路径、科目和年级等。

---

## 3️⃣ 当前数据规模 (MySQL `student_manager` 实测)

| 数据表 | 数量 | 说明 |
|------|:----:|------|
| `staff` | 27 | 1名管理员 + 26名各学部全科教师 |
| `students` | 360 | 三~六年级以及初中一~二年级，共 12 个班级，每班 30 名学生 |
| `classes` | 12 | 8个小学班级 + 4个初中班级 |
| `exams` | 72 | 历次月考及期中期末考试发布记录 |
| `scores` | 9360 | 包含 12 个班级历次考试的全科成绩（含排名重算数据） |
| `schedules` | 240 | 12 个班级的每周五天、每天 8 节课的完整课表课节 |
| `attendance` | 34560 | 课堂考勤打卡明细流水记录 |
| `leave_requests`| 10 | 学生发起的请假审批记录流程 |
| `homeworks` | 5 | 教师布置的日常作业 |
| `homework_submissions` | 28 | 学生提交的作业答案及评分评语 |
| `exam_schedules` | 6 | 排考日程表记录 |
| `test_submissions` | 150 | 学生参加在线小测的自动评分提交记录 |
| `mistakes` | 48 | 学生自主搜集/录入的错题本数据 |
| `questions` | 9 | 教学题库预置题目（含难度分级） |
| `exam_papers` | 3 | 教师端使用智能组卷工具生成的考卷记录 |
| `resources` | 3 | 教学资源库课件下载记录 |

---

## 4️⃣ 主要 API 路由汇总

### 🔑 认证与用户
* `POST /api/v1/auth/login`：登录（集成了验证码验证，自动分流角色）
* `GET /api/v1/auth/me`：获取当前用户信息
* `GET/POST /api/v1/users/students`：学生列表查询及创建
* `GET/POST /api/v1/users/staff`：教职工列表查询及创建

### 📊 成绩管理
* `GET /api/v1/scores/my`：**学生**当前学生的全部成绩
* `GET /api/v1/scores/trend`：**学生**成绩趋势数据（柱状/折线图）
* `GET /api/v1/scores/class-scores`：**教师**全班成绩（支持批量编辑录入）
* `GET /api/v1/scores/class-stats/{exam_id}`：**教师**班级成绩分析（最高/最低/均分/及格率/优秀率/分布）
* `GET /api/v1/scores/export`：**管理端**全校成绩 CSV 导出（已加入 UTF-8 BOM 修复 Excel 乱码）

### 📅 课表管理
* `GET /api/v1/schedule/my`：**学生**获取自己班级的课表
* `GET /api/v1/schedule/class/{class_id}`：**教师/管理**获取班级课表
* `PUT /api/v1/schedule/batch`：**管理端**智能排课批量微调与保存

### 📝 作业模块
* `GET /api/v1/homework/my`：**学生**查询班级布置的作业
* `POST /api/v1/homework/submit`：**学生**提交作业解答
* `GET /api/v1/homework/list`：**教师**查看自己布置的作业列表
* `PUT /api/v1/homework/submissions/{id}/grade`：**教师**给学生作业打分和评语
* `GET /api/v1/homework/overview`：**管理端**作业提交率及全校布置量统计监控

### ⏱️ 请假与考勤
* `GET /api/v1/attendance/my`：**学生**考勤看板统计及流水
* `POST /api/v1/attendance/leave-request`：**学生**申请请假（支持移动端样式）
* `POST /api/v1/attendance/roll-call`：**教师**点名考勤数据保存
* `PUT /api/v1/attendance/leave-approve/{id}`：**教师**请假审批（自动同步修改考勤）
* `GET /api/v1/attendance/overview`：**管理端**考勤异常及缺勤风控预警看板

---

## 5️⃣ 前端关键文件结构

```
frontend/src/
├── api/
│   ├── auth.ts            # 登录及验证码 API
│   ├── scores.ts          # 成绩查询及批量录入
│   ├── schedule.ts        # 课表查询与排课保存
│   ├── homework.ts        # 作业列表、提交及批改
│   ├── attendance.ts      # 课堂点名、请假申请与审批
│   └── teaching.ts        # 资源库上传下载、题库与智能组卷
├── views/
│   ├── student/
│   │   ├── Learn.vue      # 学生学习页主体（带 GSAP 卡片翻转和详情折叠动画）
│   │   ├── Scores.vue     # 成绩柱状/折线图诊断 (Chart.js)
│   │   ├── Schedule.vue   # 周课表彩色网格视图
│   │   ├── Homework.vue   # 作业卡片、答案在线提交
│   │   ├── Mistakes.vue   # 错题待复习/已掌握分组管理
│   │   ├── Attendance.vue # 考勤仪表盘与移动端高保真请假条
│   │   └── Profile.vue    # 学生个人画像
│   ├── teacher/
│   │   ├── ScoresManage.vue # 成绩录入表格与成绩统计分析
│   │   ├── HomeworkManage.vue # 作业布置、提交监控与行内评分评语
│   │   ├── ExamPaperManage.vue # 题库筛选与一键智能组卷预览
│   │   ├── ResourceLibrary.vue # 教学课件资料分类下载与上传
│   │   └── Schedule.vue   # 教师课表切换与编辑
│   └── admin/
│       ├── Users.vue      # 教职工及学生主体 CRUD 弹窗管理
│       ├── DataDashboard.vue # 全校考勤、作业及成绩数据大屏 (Chart.js 复合图表)
│       └── SmartSchedule.vue # 智能排课（一键无冲突排课算法及表格格子微调）
```

---

## 6️⃣ 后端关键文件结构

```
backend/backend/
├── models/
│   ├── staff.py, student.py, class_model.py, teacher_class.py # 主体模型
│   ├── score.py, exam.py, schedule.py                         # 教学核心模型
│   ├── homework.py, mistake.py, attendance.py                  # 日常教务模型
│   ├── exam_schedule.py, test_submission.py                    # 考试与测试模型
│   └── teaching.py                                             # 教学增强模型 (题库/试卷/资源)
├── routers/
│   ├── auth.py            # 认证（密码 bcrypt 处理及验证码生成）
│   ├── users.py           # 用户 CRUD API
│   ├── scores.py          # 成绩曲线、批量保存与 CSV 导出
│   ├── schedules.py       # 班级/教师课表查询与批量排课写入
│   ├── homework.py        # 作业生命周期流转 API
│   ├── mistakes.py        # 错题录入及教师班级高频错题汇总
│   ├── attendance.py      # 点名保存、请假处理与审批
│   └── teaching.py        # 题库筛选、自动组卷逻辑、文件上传下载
├── main.py                # FastAPI 初始化，中间件跨域及全部路由注册
```

---

## 7️⃣ 权限校验逻辑

1. **管理员 (role=admin)**：拥有全局数据视图，可进行用户 CRUD、智能排课、查看全校考勤/作业大屏、导出成绩。
2. **班主任 (homeroom_teacher_id = staff.id)**：可查看和管理本班所有科目成绩，审批本班学生请假，进行日常课堂点名。
3. **科任老师 (teacher_classes 外键关联)**：仅能管理其所教班级的对应科目成绩、作业和智能排卷。
4. **学生 (student)**：仅能访问自己班级的课表和作业，以及录入并查看自己的成绩、考勤、错题，提交个人请假申请。

---

## 8️⃣ 下一步工作

### 🚀 阶段 5.0 — AI 智能分析 (DeepSeek API 接入)
* **成绩诊断报告**：提取学生成绩数据，调用 AI 生成强弱科目分析及复习建议。
* **学情下滑智能预警**：检测连续两次及以上下滑的科目，并由 AI 给出辅导策略。
* **考勤及表现异常预警**：对频繁缺勤/请假或作业提交迟缓的学生进行触发式分析。
* **错题薄弱点智能分析**：结合错题本中录入的题干与分类，分析出薄弱的知识点脉络。
* **期末评语一键生成**：结合学生的成绩表现、出勤率、作业完成质量，由 AI 生成个性化的期末操行评语。
* **教师智能助手**：接入 Chat 对话，允许教师针对班级学情大屏数据提问（如“如何提升三1班的数学及格率？”）。
