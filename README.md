# 智慧学生管理系统

> 面向中小学教育场景的智慧学生管理系统，覆盖学生、教师、管理员三种角色，提供从日常教务到学情分析的全流程数字化解决方案。

## 技术栈

| 层级 | 技术方案 |
|------|---------|
| **前端** | Vue 3 + TypeScript + Element Plus + Pinia + Vue Router |
| **后端** | Python FastAPI + SQLAlchemy + JWT |
| **数据库** | SQLite（开发）/ MySQL（生产） |
| **动画** | GSAP（导航滑动指示条） |
| **AI** | LangChain + DeepSeek API（后期接入） |

## 项目结构

\\\
student-manager/
├── frontend/          # Vue 3 前端
│   ├── src/
│   │   ├── api/       # API 请求封装
│   │   ├── components/# 公共组件
│   │   ├── router/    # 路由配置
│   │   ├── stores/    # Pinia 状态管理
│   │   ├── styles/    # 全局样式
│   │   ├── views/     # 页面组件
│   │   └── utils/     # 工具函数
│   └── ...
├── backend/           # FastAPI 后端
│   ├── routers/       # 路由模块
│   ├── models/        # 数据库模型
│   ├── schemas/       # Pydantic 数据模型
│   ├── services/      # 业务逻辑
│   └── ...
└── docs/              # 项目文档
\\\

## 开发环境要求

- Node.js >= 18
- Python >= 3.10
- npm / pnpm

## 快速开始

### 前端

\\\ash
cd frontend
npm install
npm run dev
\\\

### 后端

\\\ash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload
\\\

## 开发规范

- 前端使用 \<script setup lang="ts">\ + Composition API
- 后端按模块组织路由和模型
- 每个功能模块独立分支开发，合并到 main
- 视觉设计先出 HTML 原型确认后再编码

## 许可

MIT
