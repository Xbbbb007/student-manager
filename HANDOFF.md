# 🤝 项目交接文档

> 供下一位接手 Agent 快速了解上下文，避免从头翻代码。
>
> 📋 **详细功能计划请看 [PLAN.md](PLAN.md)**

---

## 1️⃣ 当前状态

| 项目 | 值 |
|------|----|
| 已完成阶段 | **0~4.2**（环境搭建 / 设计系统 / 导航栏 / 认证 / 用户管理）+ **成绩管理（教师端+学生端）** |
| 下一阶段 | **4.2 续** — 学生端学习模块其他子功能（作业/考试安排/错题本/课表） |
| 当前分支 | `main` |
| 数据库 | MySQL `student_manager`（5 张表：staff, students, classes, exams, scores） |

---

## 2️⃣ 数据库表结构

### staff — 教职工（管理员 + 教师）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增 |
| username | VARCHAR(50) UNIQUE | 登录名 |
| password_hash | VARCHAR(128) | bcrypt 加密 |
| password_plain | VARCHAR(128) | 明文密码（调试用） |
| name | VARCHAR(50) | 姓名 |
| role | ENUM('teacher','admin') | |
| gender | ENUM('male','female') | 可选 |
| subject | ENUM('chinese','math','english','science','ethics') | 任教科目 |

**权限逻辑**：
- **管理员**：可查看和编辑所有班级、所有科目的成绩
- **班主任**（classes.homeroom_teacher_id → staff.id）：可查看和编辑本班所有科目的成绩
- **科任老师**（staff.subject）：只能查看和编辑自己所教科目的成绩

### students — 学生

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增 |
| username | VARCHAR(50) UNIQUE | 8位学号 |
| password_hash | VARCHAR(128) | bcrypt 加密 |
| password_plain | VARCHAR(128) | 明文密码（调试用） |
| name | VARCHAR(50) | 姓名 |
| gender | ENUM('male','female') | 可选 |
| class_id | INT FK → classes.id | 所属班级 |

### classes — 班级

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增 |
| name | VARCHAR(50) | 班级全称（如"小学部三年级一班"） |
| section | VARCHAR(20) | 学部（小学部/初中部） |
| grade | VARCHAR(20) | 年级 |
| homeroom_teacher_id | INT FK → staff.id | 班主任 |

### exams — 考试

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增 |
| name | VARCHAR(100) | 考试名称（如"第一次月考"） |
| class_id | INT FK → classes.id | 所属班级 |
| exam_date | DATE | 考试日期 |
| created_at | DATETIME | 创建时间 |

### scores — 成绩

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 自增 |
| student_id | INT FK → students.id | 学生 |
| exam_id | INT FK → exams.id | 考试 |
| subject | ENUM('chinese','math','english','science','ethics') | 科目 |
| score | DECIMAL(5,2) | 分数（0~100） |
| class_rank | INT | 班内排名（DENSE_RANK，同分并列） |
| school_rank | INT | 年级排名（同年级所有班一起排） |

---

## 3️⃣ 当前数据

| 类型 | 数量 | 说明 |
|------|:----:|------|
| 管理员 | 1 | admin / admin123 |
| 教师 | 26 | 小学部20人（4年级×5科）+ 初中部6人（2年级×3科） |
| 班级 | 12 | 小学部8班（三年级~六年级×2）+ 初中部4班（一年级~二年级×2） |
| 学生 | 360 | 学号 01030101~01060230，密码 123456 |
| 考试 | 6 | 一班：第一次月考~期末考试 |
| 成绩 | 2700 | 6次 × 5科 × 90人（一班+二班） |

### 学号规则

```
SS GG CC NN
学部 年级 班级 序号
01=小学部  02=初中部
01~06=一~六年级
01=一班  02=二班
01~30=班级内流水号
```

示例：`01050105` = 小学部五年级一班第5人

---

## 4️⃣ API 路由

### 认证

| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 登录（自动识别 staff/student） |
| GET | `/api/v1/auth/me` | 获取当前用户信息（含 subject, user_type） |

### 用户管理

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/api/v1/users/` | 合并列表（staff+students，兼容旧前端） |
| GET/POST | `/api/v1/users/staff` | 教职工列表 / 创建 |
| PUT/DELETE | `/api/v1/users/staff/{id}` | 更新 / 删除教职工 |
| GET/POST | `/api/v1/users/students` | 学生列表 / 创建 |
| PUT/DELETE | `/api/v1/users/students/{id}` | 更新 / 删除学生 |

### 班级

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/api/v1/classes/` | 班级列表（教师和管理员可访问） |

### 考试

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/api/v1/exams/` | 考试列表（支持 class_id 过滤） |
| POST | `/api/v1/exams/` | 创建新考试 |

### 成绩

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/api/v1/scores/my` | **学生**当前学生的全部成绩 |
| GET | `/api/v1/scores/trend` | **学生**成绩趋势数据 |
| GET | `/api/v1/scores/ranking/{exam_id}` | **学生**班级排名 |
| GET | `/api/v1/scores/class-scores` | **教师**全班成绩（需 exam_id + subject + class_id） |
| PUT | `/api/v1/scores/batch` | **教师**批量录入/更新成绩（自动重算排名） |
| GET | `/api/v1/scores/class-stats/{exam_id}` | **教师**班级统计（平均分/及格率/优秀率/分布） |

---

## 5️⃣ 前端关键文件

| 文件 | 说明 |
|------|------|
| `src/api/scores.ts` | 成绩 API（学生+教师全部接口） |
| `src/api/http.ts` | Axios 实例 + 拦截器 |
| `src/views/teacher/ScoresManage.vue` | **新增** 教师端成绩管理页（筛选+编辑表格+统计卡片） |
| `src/views/teacher/Layout.vue` | 教师端导航（新增"成绩"入口） |
| `src/views/teacher/Teach.vue` | 教学占位页 |
| `src/views/student/Scores.vue` | 学生端成绩（趋势图+雷达图+排名+表格） |
| `src/router/index.ts` | 路由（教师端新增 /teacher/scores） |
| `src/stores/user.ts` | 用户状态 Pinia store |
| `src/types/index.ts` | 类型定义（UserInfo 新增 subject, user_type 等字段） |

---

## 6️⃣ 后端关键文件

| 文件 | 说明 |
|------|------|
| `routers/scores.py` | 成绩路由（学生端 3 个 + 教师端 3 个 API） |
| `routers/exams.py` | **新增** 考试路由（GET 列表 + POST 创建） |
| `routers/auth.py` | 登录 / me（me 接口新增返回 subject 字段） |
| `schemas/user.py` | 用户 schema（StaffInfo 新增 subject） |
| `schemas/exam.py` | **新增** 考试 schema |
| `main.py` | 注册 exams_router |

---

## 7️⃣ 权限模型

```
登录 → 获取角色
  ├── 管理员 (role=admin)
  │   └── 所有班级 × 所有科目
  │
  ├── 班主任 (classes.homeroom_teacher_id = staff.id)
  │   └── 本班所有科目
  │
  └── 科任老师 (staff.subject = "chinese" / "math" / ...)
      └── 所有班级 × 自己科目
```

**注意**：目前教师-班级关联尚未精确到"某老师只教某班"，科任老师能看到所有班级但只能编辑自己科目的成绩。

---

## 8️⃣ 下一步工作

### 待实现

- 作业列表与提交 → 需后端 homework 表 + API
- 考试安排查看 → 需后端 exams 表扩展 + API
- 错题本 → 需后端 mistakes 表 + API
- 课表展示 → 需后端 schedule 表 + API
- 初中部补齐科学+道德教师（目前初中部仅语数英）
- 教师-班级关联表（精细化权限控制）
- 成绩 Excel 导入/导出

### 注意事项

1. 每个子功能先出 HTML 原型确认
2. 后端先建表，再写 API，前端最后对接
3. 前端路由前缀 `/student/`
4. 学生登录用学号 + 123456（如 `01030106 / 123456`）
5. 排名使用 DENSE_RANK（同分并列），不是 ROW_NUMBER
6. 教师端成绩页通过 `/teacher/scores` 访问

---

## 9️⃣ 联系

- GitHub: https://github.com/Xbbbb007/student-manager
- PRD: `智慧学生管理系统-PRD-V1.3.docx`
