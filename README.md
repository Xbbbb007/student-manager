# 智慧学生管理系统 v1.0

> 基于 **Java SE + JDBC + MySQL** 的终端驱动型学生信息管理系统，采用分层 MVC 架构，支持管理员、教师、学生三种角色，覆盖高校日常教务管理的核心业务流程。

---

## 技术栈

| 技术 | 说明 |
|------|------|
| **Java SE 17** | 项目运行环境 |
| **JDBC** | 数据库访问层 |
| **MySQL 8.x** | 持久化存储 |
| **mysql-connector-java 8.0.28** | MySQL 官方 JDBC 驱动（唯一外部依赖） |
| **自实现连接池** | `SimpleConnectionPool`，无需第三方连接池框架 |
| **MD5 + Salt 加密** | 用户密码安全存储 |

---

## 项目结构

```
shixun/
├── src/
│   └── com/sms/
│       ├── App.java                # 程序入口，含登录路由
│       ├── controller/             # 控制层（管理员 / 教师 / 学生）
│       ├── service/                # 业务服务层（接口 + 实现）
│       ├── dao/                    # 数据访问层（接口 + 实现）
│       ├── entity/                 # 实体类（13个实体 + UserRole枚举）
│       ├── util/                   # 工具类（DB连接 / 控制台 / MD5 / CSV）
│       └── exception/              # 自定义异常（4种业务异常）
├── lib/
│   └── mysql-connector-java-8.0.28.jar
├── out/                            # 编译输出目录（.class 文件）
├── db/
│   ├── init.sql                    # 建库建表脚本
│   ├── seed.sql                    # 基础测试数据
│   └── seed_extended.sql           # 扩展测试数据
├── config/
│   └── db.properties               # 数据库连接配置
├── compile.bat                     # 一键编译脚本
└── run.bat                         # 一键运行脚本
```

---

## 系统架构

```
┌────────────────────────────────────────────┐
│           View 层（终端菜单交互）              │
│   菜单驱动、表格输出、输入校验、分页展示         │
├────────────────────────────────────────────┤
│           Controller 层                     │
│   Admin / Teacher / Student 三端控制器       │
├────────────────────────────────────────────┤
│           Service 层                        │
│   UserService / AdminService /              │
│   AcademicService / EducationService        │
├────────────────────────────────────────────┤
│           DAO 层（13 个 DAO + Impl）          │
│   PreparedStatement 防注入 / 手动事务管理     │
├────────────────────────────────────────────┤
│           MySQL 数据库                       │
│   student_manager_db（13 张数据表）           │
└────────────────────────────────────────────┘
```

---

## 功能模块概览

| 模块 | 管理员 | 教师 | 学生 |
|------|:------:|:----:|:----:|
| 用户登录 / 密码安全 | ✅ | ✅ | ✅ |
| 学生信息管理（增删改查/CSV导入导出） | ✅ | — | — |
| 教师信息管理 | ✅ | — | — |
| 班级管理 | ✅ | — | — |
| 课程管理 | ✅ | — | — |
| 教学计划管理 | ✅ | — | — |
| 课表排课（含冲突检测） | ✅ | 查看 | 查看 |
| 成绩管理（录入/统计/GPA） | ✅ | ✅ | 查看 |
| 考勤管理（点名/请假审批） | ✅ | ✅ | 查看/申请 |
| 公告通知（发布/查看） | ✅ | ✅ | 查看 |
| 数据统计与报表 | ✅ | — | — |
| 自主选课 / 退课 | — | — | ✅ |

---

## 数据库

- **库名**：`student_manager_db`
- **共 13 张数据表**：`user` / `student` / `teacher` / `department` / `major` / `class` / `course` / `teaching_plan` / `score` / `attendance` / `schedule` / `leave_request` / `notice`

---

## 快速启动

### 前置条件

- Java 17+（已配置 `JAVA_HOME`）
- MySQL 8.x 服务已启动

### 第一步：初始化数据库

```sql
source db/init.sql
source db/seed.sql
```

### 第二步：确认数据库配置

编辑 `config/db.properties`：

```properties
db.url=jdbc:mysql://localhost:3306/student_manager_db?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=GMT%2B8
db.username=root
db.password=123456
```

### 第三步：编译（如需重新编译）

双击或执行 `compile.bat`

### 第四步：启动系统

双击或执行 `run.bat`

---

## 默认登录账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| `admin` | `admin123` | 系统管理员 |
| `teacher1` | `teacher123` | 教师（王建国·教授） |
| `teacher2` | `teacher123` | 教师（刘秀英·副教授） |
| `student1` | `student123` | 学生（李明） |
| `student2` | `student123` | 学生（张强） |

> 密码使用 MD5 + 随机盐值加密存储，连续登录失败 5 次将触发账户锁定。

---

## 预置测试数据规模

| 数据类别 | 数量 |
|----------|------|
| 院系 | 5 个 |
| 专业 | 10 个 |
| 班级 | 12 个 |
| 教师 | 10 名（含教授/副教授/讲师） |
| 学生 | 56 名 |
| 课程 | 16 门（必修/选修/公选） |
| 成绩记录 | 78 条 |
| 考勤记录 | 45 条 |
| 请假申请 | 6 条 |
| 公告通知 | 6 条 |

---

详细功能说明请查阅 [detail.md](./detail.md)
