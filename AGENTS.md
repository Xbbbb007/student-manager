# 智慧学生管理系统 — Agent 开发指导手册

> 本文档是开发规范。**详细功能计划请看 `PLAN.md`**。
> **核心原则：每一步都要小步推进、确认后再继续。**

---

数据库 root 123456

数据库名称student_manager

## 铁律（每次对话开始时必读）

1. **一次只做一个阶段**，当前阶段未完成并得到用户确认前，禁止进入下一阶段
2. **模块优先，角色次之**：一个功能模块包含学生/教师/管理三端，一起开发
3. **共享数据层**：同一张表 + 同一套 API，不同角色通过权限过滤数据
4. **视觉决策必须先出原型**：配色、布局、组件样式等，先出 HTML 原型确认后再写入项目
5. **主动提问，不要猜**：遇到设计选择必须停下来问用户
6. **每个阶段结束时汇报**：做了什么、有什么问题、下一步计划

---

## 项目概览

- **项目类型**：前后端分离的全栈 Web 应用
- **技术栈**：Vue 3 + TypeScript + Element Plus + Pinia / Python FastAPI + SQLAlchemy + MySQL + JWT + bcrypt / GSAP + Chart.js
- **AI 模块**：后期建设，核心功能稳定后再接入 DeepSeek API
- **三种角色**：学生端、教师端、管理端（共用一套导航栏组件）
- **教师端细分为**：班主任（看所有科目）vs 科任老师（只看自己教的科目）

---

## 代码规范

### 前端

- 组件用 `<script setup lang="ts">` + Composition API
- 样式用 `<style scoped>`，全局变量在 `variables.scss`
- 路由按模块组织：`/student/learn/*`、`/teacher/scores`、`/admin/*`
- API 请求统一封装在 `src/api/` 目录
- 提交作业用 Pinia store 管理用户状态

### 后端

- 按模块组织 router：`routers/auth.py`、`routers/scores.py`、`routers/exams.py` 等
- 数据库模型在 `models/`，Pydantic schema 在 `schemas/`
- 所有接口加类型注解，确保 Swagger 文档完整
- 密码用 bcrypt（不用 passlib，避免兼容性问题）
- 权限检查：在 router 层校验 user_type + role + subject

### 数据库

- 开发和生产统一用 MySQL（`student_manager`，root/123456）
- 用 SQLAlchemy ORM 管理表结构
- 种子数据通过 `seed_data.py` 维护

---

## 权限模型（通用）

```
学生 (user_type=student)
  └── 只能查看自己的数据

科任老师 (user_type=staff, subject=具体科目)
  └── 可查看/编辑所教科目的所有班级数据

班主任 (user_type=staff, homeroom_teacher_id 匹配)
  └── 可查看/编辑本班所有科目的数据

管理员 (user_type=staff, role=admin)
  └── 所有数据的全局视图
```

---

## 每阶段结束时的汇报模板

```
✅ 本阶段完成：[阶段名称]

已完成：
- [具体完成的事项]

遇到的问题（如有）：
- [问题和解决方案]

下一阶段计划：
- [下一步要做什么]

请确认后我继续下一步。
```

---

## 禁止事项

- ❌ 禁止一次性写完所有代码再测试
- ❌ 禁止在用户没确认的情况下就用默认设计
- ❌ 禁止跳过原型直接写 Vue 组件
- ❌ 禁止并行开发多个模块
- ❌ 禁止在 AI 模块之前就把 AI 相关代码写进去
- ❌ 禁止用 `passlib`（与 bcrypt >= 5.0 不兼容，直接用 `bcrypt` 库）
- ❌ 禁止硬编码密码或密钥到代码中（开发阶段的默认值除外，但需注释说明）
