<div align="center">

# 🎯 ProView AI Interviewer

**用 AI 重新定义面试准备 — 模拟、分析、提升，一站式搞定**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/nicepkg/nicegui/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Flask](https://img.shields.io/badge/Flask-3-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Supabase](https://img.shields.io/badge/Supabase-Postgres-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com)

[快速开始](#-快速开始) · [功能特性](#-功能特性) · [技术架构](#-技术架构) · [部署指南](#-部署指南) · [文档](docs/)

</div>

---

## 📖 项目简介

ProView AI Interviewer 是一个面向求职者的 **AI 模拟面试平台**。上传简历，选择目标岗位，即可获得 AI 驱动的实时模拟面试、多维度评估报告和个性化职业发展建议。

无需注册、无需付费，本地一键部署即可使用。

> 💡 **适合谁？** 正在准备校招/社招面试的开发者、产品经理、运营等互联网从业者。

---

## ✨ 功能特性

### 🎙️ AI 模拟面试

- **多岗位适配**：前端、后端、产品、运营等，自动匹配面试风格
- **流式交互**：SSE 实时推送，AI 回答过程可见、可控、可中断
- **多维度评估**：面试结束后自动生成技术、表达、逻辑等维度的评分报告
- **灵活配置**：支持自定义面试难度、风格、AI 模型提供商

### 📄 简历智能分析

- **多格式 OCR**：支持 PDF、Word、图片（含 HEIC）等多格式简历上传
- **自动解析**：AI 提取简历关键信息，生成结构化摘要
- **优化建议**：基于目标岗位自动生成简历优化方案
- **简历编辑器**：在线编辑简历，支持 Markdown/HTML 导出 PDF

### 📊 职业发展规划

- **能力画像**：基于面试历史和简历自动生成个人能力画像
- **智能规划**：围绕目标岗位生成 3~12 个月的个性化发展路径
- **里程碑追踪**：分阶段设定目标，任务看板跟踪执行进度
- **知识文档库**：提供面试技巧、行业知识等结构化学习资料

### 🔧 开发者友好

- **调试面板**：可查看 System Prompt、RAG 命中、评估草稿等调试信息
- **RAG 知识增强**：支持向量检索增强，让 AI 面试官更专业
- **多模型支持**：DeepSeek、文心一言等，可灵活切换

---

## 🚀 快速开始

> ⚡ 5 分钟从零到运行，只需 3 步。

### 前置要求

- Python 3.11+
- Node.js 18+

### Step 1：克隆项目

```bash
git clone https://github.com/your-username/ProView-AI-Interviewer.git
cd ProView-AI-Interviewer
```

### Step 2：配置后端

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env    # Windows PowerShell
# cp .env.example .env    # macOS / Linux
```

编辑 `backend/.env`，至少配置以下一项：

```env
# 大模型（必选其一）
DEEPSEEK_API_KEY=sk-xxx
# ERNIE_API_KEY=xxx

# 存储（必选其一）
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
```

启动后端：

```bash
python -m playwright install chromium   # 首次需要
python app.py                            # → http://localhost:5000
```

### Step 3：启动前端

```bash
cd frontend
npm install
npm run dev    # → http://localhost:5173
```

打开浏览器访问 `http://localhost:5173/app.html`，开始使用。

---
## 界面预览

![面试配置界面](img/fa674dc496310c55a107fa5ab104938.png)

![评估报告界面](img/cc8ee88dbf82050a13d88268752e583.png)

![简历生成工作台](img/83192b99831554bba147f0ede46f79b.png)


## 🏗️ 技术架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Vue 3 +    │ SSE │   Flask +    │ SQL │   Supabase   │
│  TypeScript  │◄───►│   LangChain  │◄──►►│  PostgreSQL  │
│   Frontend   │     │   Backend    │     │   (可选直连)  │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────┴───────┐
                     │              │
                ┌────▼────┐   ┌────▼────┐
                │  DeepSeek │  │  文心一言  │
                │  (LLM)   │  │  (LLM)   │
                └─────────┘   └─────────┘
```

| 层级 | 技术选型 |
|------|----------|
| 前端 | Vue 3 + TypeScript + Vite + Pinia + TailwindCSS |
| 后端 | Flask + LangChain + SSE + Playwright |
| 数据库 | Supabase / PostgreSQL（支持 HTTP 直连两种模式） |
| AI 模型 | DeepSeek / 文心一言（可扩展） |
| OCR | PaddleOCR |
| 语音 | 百度语音（可选） |

---

## 📁 项目结构

```
ProView-AI-Interviewer/
├── frontend/          # Vue 3 前端（面试界面、简历编辑器、职业规划）
├── backend/           # Flask 后端（AI 编排、SSE 流、存储、OCR）
│   ├── services/      # 业务逻辑（面试、简历分析、职业规划）
│   ├── data/          # 本地数据（SQLite 职业规划库）
│   └── app.py         # 入口文件
├── ai_interview_agent/# AI 面试 Agent 提示词模板
├── docs/              # 文档（架构、数据库、运维、功能说明）
├── LICENSE            # Apache 2.0
└── README.md
```

---

## 🌐 部署指南

### 前后端分离部署

前端通过环境变量指定后端地址：

```env
VITE_API_BASE_URL=https://your-backend.example.com
```

### 存储方案

| 方案 | 适用场景 | 配置 |
|------|----------|------|
| **Supabase HTTP**（推荐） | 云端部署 | `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` |
| **直连 PostgreSQL** | 本地开发 | `BACKEND_DB_URL`（完整连接串） |

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [数据库配置指南](docs/database/SUPABASE_SETUP_GUIDE.md) | Supabase 初始化与 RAG 配置 |
| [架构文档](docs/architecture/) | 系统设计、模块拆分、数据流 |
| [API 调用映射](docs/BACKEND_FRONTEND_API_CALL_MAP.md) | 前后端接口对照表 |
| [功能说明](docs/features/) | 各功能模块详细设计 |
| [运维手册](docs/runbooks/) | 部署、监控、故障处理 |

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request。开发前请阅读 [贡献指南](docs/README.md)。

---

## 📄 License

[Apache License 2.0](LICENSE)

---

<div align="center">

**用 AI 加速你的职业成长 ⭐**

如果这个项目对你有帮助，请给一个 Star ⭐

</div>
