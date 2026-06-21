# 🤝 项目交接文档

> 供下一位接手 Agent 快速了解上下文，避免从头翻代码。

---

## 1️⃣ 当前状态

| 项目 | 值 |
|------|----|
| 已完成阶段 | **0~4.1**（环境搭建 / 设计系统 / 导航栏 / 认证 / 用户管理）+ **4.2 UI 框架** |
| 下一阶段 | **4.2 学生端—学习模块**（子功能后端对接） |
| 当前分支 | `main` |
| 数据库 | MySQL `student_manager`（3 张表：staff, students, classes） |

---

## 2️⃣ 数据库表结构（2024-06-21 重构）

> 从单表 `users` 重构为 `staff` + `students` 双表

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
| subject | ENUM('chinese','math','english') | 可选 |

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

### 学号规则

```
SS GG CC NN
学部 年级 班级 序号
01=小学部  02=初中部
01~04=一~四年级
01=一班  02=二班
01~30=班级内流水号
```

示例：`02010120` = 初中部一年级二班第20人

---

## 3️⃣ 当前数据

| 类型 | 数量 |
|------|:----:|
| 管理员 | 1（admin / admin123） |
| 教师 | 12（zhang_laoshi 等，密码 123456） |
| 班级 | 8（小学部4班 + 初中部4班） |
| 学生 | 240（学号 01030101~02020230，密码 123456） |

---

## 4️⃣ API 路由

| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 登录（自动识别 staff/student） |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |
| GET | `/api/v1/users/` | 合并列表（staff+students，兼容旧前端） |
| GET/POST | `/api/v1/users/staff` | 教职工列表 / 创建 |
| PUT/DELETE | `/api/v1/users/staff/{id}` | 更新 / 删除教职工 |
| GET/POST | `/api/v1/users/students` | 学生列表 / 创建 |
| PUT/DELETE | `/api/v1/users/students/{id}` | 更新 / 删除学生 |
| GET | `/api/v1/classes/` | 班级列表 |

**认证方式**：Bearer Token，JWT 载荷含 `user_type`（staff/student）。

---

## 5️⃣ 前端关键文件

| 文件 | 说明 |
|------|------|
| `src/api/users.ts` | 用户相关 API（list, create, update, delete） |
| `src/api/classes.ts` | 班级 API |
| `src/views/admin/Users.vue` | 用户管理页（教职工 + 学生双视图） |
| `src/views/admin/Layout.vue` | 管理端布局 |
| `src/views/student/Learn.vue` | 学生学习首页（Hero Grid + 模块进入动画 + 子模块框架） |
| `src/views/student/Layout.vue` | 学生端布局（GSAP Flip 导航 + 模块模式切换） |
| `src/views/Login.vue` | 登录页 |
| `src/router/index.ts` | 路由 + 登录守卫 |
| `src/stores/user.ts` | 用户状态 Pinia store |

---

## 6️⃣ 后端关键文件

| 文件 | 说明 |
|------|------|
| `models/staff.py` | Staff 模型 |
| `models/student.py` | Student 模型 |
| `models/class_model.py` | Class 模型 |
| `models/enums.py` | StaffRole, Gender, Subject 枚举 |
| `routers/auth.py` | 登录 / me 接口 |
| `routers/users.py` | 用户 CRUD（staff + students + legacy） |
| `routers/classes.py` | 班级接口 |
| `services/auth.py` | 认证 + 创建用户逻辑 |
| `core/security.py` | JWT + bcrypt |

---

## 7️⃣ 下一步工作：阶段 4.2 续 — 学生端·学习模块子功能实现

### 已完成（UI 框架）

- Hero 首页：名言翻转卡片 + 五模块入口 Grid 布局
- GSAP 动画：进入模块 / 标签切换 / 返回首页
- 导航栏联动：主导航 ↔ 模块标签自动切换（provide/inject + 回调注册）
- 子模块内容区框架就绪

### 待实现

- 成绩查询（表格 + 折线图）→ 需后端 scores 表 + API
- 作业列表与提交 → 需后端 homework 表 + API
- 考试安排查看 → 需后端 exams 表 + API
- 错题本 → 需后端 mistakes 表 + API
- 课表展示 → 需后端 schedule 表 + API

### 注意事项

1. 每个子功能先出 HTML 原型确认
2. 后端先建表，再写 API，前端最后对接
3. 前端路由前缀 `/student/`
4. 当前登录用 `admin/admin123` 测试，学生端需要先用学生账号登录（如 `01030101 / 123456`）

---

## 8️⃣ 联系

- GitHub: https://github.com/Xbbbb007/student-manager
- PRD: `智慧学生管理系统-PRD-V1.3.docx`
