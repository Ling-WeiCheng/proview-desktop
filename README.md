# ProView Desktop

ProView 是一个本地优先的 AI 求职训练工作台。这个仓库同时包含：

- Web 前端：`frontend/`，基于 Vue 3 + Vite
- Python 后端：`backend/`，基于 Flask
- 桌面壳：`desktop/`，基于 Electron

它不是单一的“AI 模拟面试”演示，而是一套完整的本地求职工具，覆盖面试训练、简历处理、简历优化、简历生成和职业规划等能力。

如果你只是想直接体验桌面版，可前往测试版发布页下载：

- [GitHub Releases](https://github.com/gravel-01/proview-desktop/releases)

首次启动后，请先在应用内填写你自己的模型、OCR 和语音服务密钥。

## 核心能力

- AI 模拟面试：面试配置、实时对话、总结报告、历史记录
- 简历处理：上传、OCR 解析、预览、本地管理
- 简历优化：问卷引导、AI 建议、定向优化
- 简历生成：多模板编辑、预览、导出
- 职业规划：生成阶段目标、任务建议与长期跟踪内容
- 双形态运行：同一套业务前后端，同时支持 Web 和桌面版

## 界面预览

![面试配置界面](img/fa674dc496310c55a107fa5ab104938.png)

![评估报告界面](img/cc8ee88dbf82050a13d88268752e583.png)

![简历生成工作台](img/83192b99831554bba147f0ede46f79b.png)

## 仓库结构

- `frontend/`：业务前端。`index.html` 是落地页，`app.html` 是应用入口。
- `backend/`：Flask API，负责面试、简历、OCR、PDF 导出、历史记录和运行时配置。
- `desktop/`：Electron 桌面壳，负责启动本地后端、加载前端构建产物并打包 Windows 版本。
- `doc/`：开发流程和说明文档。
- `img/`：README 使用的界面截图。

## 按目标阅读

- [README_WEB.md](README_WEB.md)：只做 Web 开发、前后端联调时优先看这个
- [README_DESKTOP.md](README_DESKTOP.md)：调试 Electron、桌面运行时或打包时优先看这个
- [backend/.env.example](backend/.env.example)：运行时配置示例
- [CONTRIBUTING.md](CONTRIBUTING.md)：协作与提交流程
- [SECURITY.md](SECURITY.md)：敏感信息与安全说明

## 快速开始

### 环境要求

- Python 3 + `pip`
- Node.js + `npm`
- Windows 开发环境（桌面端调试和打包推荐）

### 安装依赖

```powershell
cd backend
python -m pip install -r requirements.txt

cd ..\frontend
npm install

cd ..\desktop
npm install
```

如果你需要 PDF 导出功能，建议额外安装 Playwright 浏览器：

```powershell
cd backend
python -m playwright install chromium
```

如果你想优先复用系统 Edge：

```powershell
$env:PROVIEW_PLAYWRIGHT_CHANNEL = "msedge"
```

## Web 与桌面版的关系

两者不是两套独立系统，而是同一套业务代码的两种运行方式。

```text
Web 版
浏览器 -> frontend(Vite / dist) -> backend(Flask)

桌面版
Electron -> 启动本地 backend(Flask) -> 加载 frontend/dist/app.html
```

区别主要在于：

- Web 开发模式下，需要手动分别启动 `backend` 和 `frontend`
- 桌面版运行时，由 Electron 自动启动本地后端
- 桌面版加载的是 `frontend/dist/app.html`，不是 Vite dev server
- Web 和桌面版共用同一套业务页面，不单独维护第二套 UI

## 运行方式

### 1. Web 版开发

先启动后端：

```powershell
cd backend
python app.py
```

再启动前端：

```powershell
cd frontend
npm run dev
```

默认地址：

- 落地页：`http://localhost:5173/`
- 业务应用：`http://localhost:5173/app.html`
- 运行时配置页：`http://localhost:5173/app.html#/config`

默认后端端口为 `5000`。如果端口冲突，可在 `backend/.env` 中设置：

```env
PROVIEW_API_PORT=5000
```

### 2. 桌面版开发

桌面模式启动前，必须先构建前端资源：

```powershell
cd desktop
npm run build:frontend
```

然后启动 Electron：

```powershell
cd desktop
npx electron .
```

桌面版默认会：

1. 启动本地 `backend/app.py`
2. 使用 `http://127.0.0.1:18765` 作为本地 API 地址
3. 轮询 `/api/health`
4. 健康检查通过后加载 `frontend/dist/app.html`

如果你想指定 Python 解释器，可设置：

```powershell
$env:PROVIEW_DESKTOP_PYTHON = "D:\path\to\python.exe"
```

如果你改了前端页面，重新执行一次：

```powershell
cd desktop
npm run build:frontend
```

### 3. 打包桌面版

推荐使用仓库根目录脚本：

```powershell
.\package-desktop.ps1
```

常见用法：

```powershell
# 使用默认配置打包
.\package-desktop.ps1

# 指定 Conda 环境
.\package-desktop.ps1 -CondaEnvName my-env

# 跳过前端或后端构建
.\package-desktop.ps1 -SkipFrontend -SkipBackend

# 只构建，不执行最终打包
.\package-desktop.ps1 -SkipPackage
```

也可以直接在 `desktop/` 目录使用底层脚本：

```powershell
cd desktop
npm run dist
```

输出目录：

- `desktop/release/`

## 运行时配置

配置主要有两种写入方式：

- Web 本地开发：使用 `backend/.env`
- 桌面版运行时：使用 Electron 用户数据目录中的 `backend-data/.env`

同时，应用内的运行时配置页也可以直接保存这些配置。

常用配置项如下：

| 配置项 | 用途 | 说明 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` | DeepSeek 模型调用 | 至少配置一个模型提供商 |
| `ERNIE_API_KEY` / `ERNIE_BASE_URL` | 百度文心模型调用 | 可作为另一套模型入口 |
| `PADDLEOCR_API_URL` / `PADDLE_OCR_TOKEN` | OCR 服务 | 简历解析依赖 |
| `BAIDU_APP_KEY` / `BAIDU_SECRET_KEY` | 语音识别/合成 | 语音面试依赖 |
| `BACKEND_DB_URL` | 数据库存储 | 推荐本地 PostgreSQL；不填时会回退到 SQLite |
| `PROVIEW_API_PORT` | 后端端口 | Web 默认 `5000`，桌面默认 `18765` |

补充说明：

- 不配置模型、OCR 或语音服务时，项目仍可启动，但对应功能不可用
- 配置示例请看 [backend/.env.example](backend/.env.example)
- 模型、OCR 和语音服务密钥需要你自行申请，README 不再展开供应商开户流程

## 数据与存储

项目默认是本地优先的。

Web 本地开发时，常见数据会落在后端运行目录附近，例如：

- `backend/.env`
- 上传的简历文件
- 生成的预览或导出文件
- 本地数据库文件

桌面版运行时，常见数据会写入 Electron 用户数据目录下的 `backend-data/`，其中包括：

- 运行时 `.env`
- 数据库文件
- 上传文件和导出文件
- 后端日志

## 功能概览

### 面试训练

- 支持岗位、场景、音色等面试配置
- 支持语音实时交互与文本记录
- 面试结束后生成评估报告并保留历史记录

### 简历工作台

- 支持简历上传、OCR 解析和本地管理
- 支持按目标方向生成优化建议
- 支持在多种模板中生成并导出简历

### 职业规划

- 支持生成中长期职业规划建议
- 支持分阶段查看目标、任务与参考内容
- 当前仍在持续完善中

## 建议的阅读顺序

如果你是第一次接手这个仓库，建议按下面顺序看：

1. 先读这份 `README.md`，了解整体结构
2. 如果做业务开发，继续看 [README_WEB.md](README_WEB.md)
3. 如果做桌面调试或打包，继续看 [README_DESKTOP.md](README_DESKTOP.md)
4. 配置运行时参数时，对照 [backend/.env.example](backend/.env.example)

---

这份 README 保持为项目总入口。更细的联调、桌面启动链路和打包细节，统一放在对应子文档中维护。
