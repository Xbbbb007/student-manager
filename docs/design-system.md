# 设计系统 · Design System

> 智慧学生管理系统视觉规范文档，记录设计 Token、组件样式、布局规则。
> **修改前请先阅读此文档，保持一致性。**

---

## 1. 配色方案 —「东方青蓝」

基于中国传统色板提炼，以深邃宝蓝为主色、暖白米色为底，营造沉稳雅致的书卷气息。

### 1.1 色板

| 命名 | 色值 | 用途 | 色块 |
|------|------|------|------|
| **Royal** | `#334EAC` | 品牌主色、主按钮、导航激活态、标题强调 | 🟦 |
| **Midnight** | `#081F5C` | 深色文字、侧边栏背景、页脚 | ⬛ |
| **China** | `#7096D1` | 辅色、次要按钮、图标、Hover 态 | 🟧 |
| **Sky** | `#BAD6EB` | 边框、表格分割线、次要装饰 | 🟨 |
| **Dawn** | `#D0E3FF` | 表格 hover 行、标签背景、激活态浅底 | 🟩 |
| **Porcelain** | `#EDF1F6` | 页面主背景、表头背景 | 🟪 |
| **Moon** | `#F7F2EB` | 卡片背景、轻背景区块 | 🟫 |
| **Jicama** | `#FFF9F0` | 内容区背景、表单背景 | ⬜ |
| **Asian Pear** | `#F2F0DE` | 备用暖色、点缀 | 🟨 |

### 1.2 Token 映射

```scss
// 主色
--color-primary:       #334EAC;  // Royal
--color-primary-dark:  #081F5C;  // Midnight
--color-primary-light: #7096D1;  // China

// 背景色
--color-bg:            #EDF1F6;  // Porcelain
--color-bg-card:       #F7F2EB;  // Moon
--color-bg-content:    #FFF9F0;  // Jicama

// 边框与分割线
--color-border:        #BAD6EB;  // Sky
--color-border-light:  #D0E3FF;  // Dawn

// 功能色
--color-success:       #10B981;
--color-warning:       #E8A838;
--color-danger:        #EF4444;
--color-info:          #6B7280;

// 文字
--color-text:          #1F2937;
--color-text-secondary:#6B7280;
--color-text-light:    #9CA3AF;
```

### 1.3 使用规则

- **主色 Royal** 是唯一的品牌色，不要用其他颜色代替主要按钮和导航激活态
- **不要**在纯白背景上使用浅色文字
- 成功/警告/危险等语义色仅在对应场景使用，不用于装饰

---

## 2. 字体与排版

### 2.1 字体栈

```css
--font-family: system-ui, "Microsoft YaHei", "PingFang SC", sans-serif;
```

- 中文字体优先 `Microsoft YaHei`（Windows）和 `PingFang SC`（macOS）
- 英文字体退回到系统默认无衬线
- 代码/数字等使用等宽场景：`"Cascadia Code", "JetBrains Mono", monospace`

### 2.2 字号层级

| Token | 大小 | 行高 | 用途 |
|-------|------|------|------|
| `--font-size-xs` | 12px | 1.4 | 辅助文字、标签、提示 |
| `--font-size-sm` | 13px | 1.5 | 次要文字、表格内容 |
| `--font-size-base` | 14px | 1.5 | 正文、段落、表单标签 |
| `--font-size-lg` | 16px | 1.5 | 卡片标题、导航文字 |
| `--font-size-xl` | 18px | 1.4 | 子页面标题 |
| `--font-size-xxl` | 24px | 1.3 | 页面大标题 |

### 2.3 字重

- 正文：`400` (Regular)
- 强调：`500` (Medium)
- 标题：`600` (Semibold)
- Logo/品牌：`700` (Bold)

---

## 3. 圆角与阴影

### 3.1 圆角

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-sm` | 4px | 标签、小点缀 |
| `--radius-md` | 8px | 按钮、输入框、卡片（默认） |
| `--radius-lg` | 12px | 大卡片、弹窗、侧边栏 |

**规则**：全系统保持统一，主按钮/输入框/卡片统一 8px，不使用混合圆角。

### 3.2 阴影

| Token | 值 | 用途 |
|-------|-----|------|
| `--shadow-sm` | `0 1px 2px rgba(8,31,92,0.06)` | 导航栏、轻悬浮 |
| `--shadow-md` | `0 4px 6px rgba(8,31,92,0.08)` | 卡片默认、下拉菜单 |
| `--shadow-lg` | `0 10px 15px rgba(8,31,92,0.1)` | 弹窗、抽屉、模态框 |

**规则**：阴影使用主色的深色 `#081F5C` 作为投影色，不用纯黑，更柔和自然。

---

## 4. 组件样式规范

### 4.1 导航栏 NavBar
- 高度：56px
- 背景：`--color-bg-content`（Jicama）
- Logo 文字：18px Bold Royal
- 导航项：14px，激活态用 Royal 色填充底 + 文字加粗
- 滑动指示条：3px 高 Royal 色，CSS transition 或 GSAP 实现

### 4.2 按钮 Button
- 主要按钮：`bg: Royal` + `color: #fff`，圆角 8px
- 次要按钮：`bg: China` + `color: #fff`
- 线框按钮：`border: 1.5px China` + `color: Royal`
- 悬停态：加深或轻微上浮（`translateY(-1px)`）
- 点击态：`scale(0.98)` 模拟物理按下

### 4.3 卡片 Card
- 背景：`--color-bg-card`（Moon）
- 边框：1px solid `--color-border-light`（Dawn）
- 圆角：12px
- 内边距：20px

### 4.4 表格 Table
- 表头：背景 Porcelain，底边 2px Sky
- 表行：分割线 1px Dawn
- Hover 行：背景 Dawn
- 状态标签：圆角 12px，语义色对应

### 4.5 表单 Form
- 标签在上，输入框在下
- 输入框：边框 Sky，聚焦时边框 China + 浅蓝光晕
- 内边距：10px 14px
- 错误提示红色在输入框下方

---

## 5. 间距

| Token | 值 | 用途 |
|-------|-----|------|
| `--spacing-xs` | 4px | 极小间距，图标与文字 |
| `--spacing-sm` | 8px | 紧凑间距，标签间距 |
| `--spacing-md` | 16px | 通用间距，组件内部 |
| `--spacing-lg` | 24px | 区块间距、卡片边距 |
| `--spacing-xl` | 32px | 大区块间距、页面边距 |

---

## 6. 布局规则

- 页面内容区最大宽度 1200px，居中
- 导航栏吸顶（sticky），z-index 100
- 管理端可选用侧边栏布局，侧边栏宽度 200px
- 内容区背景 `--color-bg`，卡片区背景 `--color-bg-card`

---

## 7. 图标

- 默认使用 **Element Plus 内置图标**（通过 `ElIcon` 组件）
- 如需扩展图标库，优先选择 **Lucide** 或 **Remix Icon**
- 风格偏好：**线性（outline）**，24px 基准

---

## 8. 插画

- 空状态页面使用 **纯色块扁平插画** + 简短文字提示
- 不需要复杂插画场景，保持简洁

---

> **维护说明**：修改设计 Token 时请同步更新此文档和 `frontend/src/styles/variables.scss`。
> 颜色值以 `variables.scss` 中的 CSS 自定义属性为准。
