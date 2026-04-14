# 写在前面
打包好的单机桌面版ProView Desktop-测试版已经上线啦！快来下载预览版按照要求配置密钥开启你的AI面试助手吧！
- https://github.com/gravel-01/proview-desktop/releases/tag/v0.1.0-alpha.1
  
# ProView AI Interviewer / ProView Desktop

这是一个本地优先的 AI 求职训练工作台。仓库包含同一套业务前端、同一套 Python 后端，以及一个将它们封装为桌面应用的 Electron 外壳。

当前代码已经不只是“AI 模拟面试”，还包括：

- 面试配置、实时对话、总结报告、历史记录
- 简历上传与解析
- 简历优化
- 简历生成器
- 我的简历库与预览
- 职业规划工作台

## 仓库结构

- `frontend/`：Vue 3 + Vite 前端。`index.html` 是落地页，`app.html` 是真正的业务应用入口。
- `backend/`：Flask API。负责面试流程、简历处理、OCR、PDF 导出、历史记录、职业规划和运行时配置。
- `desktop/`：Electron 桌面壳。负责拉起本地后端、加载前端打包产物，并打包为 Windows 桌面版。
- `database/`：本地数据库文件目录。
- `doc/`：开发说明与流程文档。

## 按需开发入口

如果你是下载项目后按需开发，直接按目标选择文档：

- [README_WEB.md](README_WEB.md)：只开发 Web 版，适合前端页面、Flask API、前后端联调
- [README_DESKTOP.md](README_DESKTOP.md)：只开发桌面版，适合 Electron、桌面运行时、Windows 打包


## Web 版和桌面版的关系

两者不是两套独立系统，而是同一套前后端代码的两种运行方式。

```text
Web 版:
浏览器 -> frontend(Vite / dist) -> backend(Flask)

桌面版:
Electron -> 启动本地 backend(Flask) -> 加载 frontend/dist/app.html
```

关键区别：

- Web 版开发时，需要你手动分别启动 `backend` 和 `frontend`。
- 桌面版运行时，由 Electron 自动启动本地 `backend`，然后加载 `frontend/dist/app.html`。
- 桌面版不是单独维护一套 UI，它复用的就是 `frontend` 中的业务应用。
- Web 开发模式下，默认数据会落在仓库内的 `backend/` 目录附近。
- 桌面版运行时，数据、运行时 `.env`、SQLite 文件会落在 Electron 的用户数据目录中。

## 环境准备

建议先准备好以下基础环境：

- Python + `pip`
- Node.js + `npm`
- Windows 开发环境（桌面打包脚本当前面向 Windows）

后端依赖安装：

```powershell
cd backend
python -m pip install -r requirements.txt
```

如果你需要使用 PDF 导出功能，建议额外安装一次 Playwright 浏览器内核：

```powershell
python -m playwright install chromium
```

如果你不想安装 Playwright 自带浏览器，也可以改用系统里已有的 Edge：

```powershell
$env:PROVIEW_PLAYWRIGHT_CHANNEL = "msedge"
```

前端依赖安装：

```powershell
cd frontend
npm install
```

桌面壳依赖安装：

```powershell
cd desktop
npm install
```

## 运行时配置

后端支持通过 `.env` 和运行时配置页写入配置。Web 本地开发时通常使用 `backend/.env`；桌面版运行时会自动把配置写到桌面运行目录中的 `.env`。

常见配置项：

| 配置项 | 用途 | 是否必需 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek 模型调用 | 需要使用 DeepSeek 时必需 |
| `DEEPSEEK_BASE_URL` | DeepSeek/OpenAI 兼容网关地址 | 可选 |
| `ERNIE_API_KEY` | 百度文心模型调用 | 需要使用文心时必需 |
| `ERNIE_BASE_URL` | 文心网关地址 | 可选 |
| `PADDLEOCR_API_URL` | OCR 服务地址 | 需要 OCR 时必需 |
| `PADDLE_OCR_TOKEN` | OCR 服务令牌 | 需要 OCR 时必需 |
| `BAIDU_APP_KEY` | 百度语音配置 | 需要语音功能时必需 |
| `BAIDU_SECRET_KEY` | 百度语音配置 | 需要语音功能时必需 |
| `PROVIEW_API_PORT` | 后端监听端口 | 可选 |
| `BACKEND_DB_URL` | 外部数据库地址 | 可选 |
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | Supabase 存储接入 | 可选 |

说明：

- 不配置外部数据库时，系统会自动回退到本地 SQLite。
- 不填写模型、OCR、语音相关配置时，对应功能不可用，但项目仍可启动。
- 前端应用内有运行时配置页可直接保存这些配置。
- 如果 `PADDLEOCR_API_URL` 指向本机或局域网内的 OCR 服务，开启 VPN 全局模式可能会导致 PaddleOCR 无法连接。遇到 OCR 请求失败时，优先检查是否开启了全局代理；必要时改为规则模式，或将 OCR 服务地址加入直连/绕过代理名单。

## 启动后端

最直接、最可靠的开发启动方式是直接运行 Flask 入口：

```powershell
cd backend
python app.py
```

默认端口：

- Web 开发模式默认端口是 `5000`
- 桌面版运行时默认端口是 `18765`

如果你想自定义 Web 开发端口，可以在 `backend/.env` 中写入：

```env
PROVIEW_API_PORT=5000
```

项目里也提供了 `backend/start.bat` 和 `backend/start.sh`，但它们默认写死了一个 Conda 环境名 `3.13_langchia`，更适合作为示例脚本；通用开发建议还是直接使用 `python app.py`。

## 启动 Web 版

先确保后端已经启动，再启动前端开发服务器：

```powershell
cd frontend
npm run dev
```

常用访问地址：

- 落地页：`http://localhost:5173/`
- 业务应用：`http://localhost:5173/app.html`
- 运行时配置页：`http://localhost:5173/app.html#/config`

说明：

- `frontend` 使用的是 `app.html + hash router`，所以业务路由形如 `app.html#/interview`、`app.html#/history`。
- Vite 开发服务器会把 `/api` 请求代理到后端。
- 代理目标默认读取 `PROVIEW_API_PORT`，如果没有配置则回退到 `5000`。

如果你想构建 Web 静态产物：

```powershell
cd frontend
npm run build
npm run preview
```

构建结果位于 `frontend/dist/`，其中会同时生成：

- `index.html`：落地页
- `app.html`：业务应用入口

## 启动桌面版

桌面版本地调试不是连接 Vite 开发服务器，而是直接加载 `frontend/dist/app.html`。因此启动前必须先构建前端。

### 1. 准备 Python 后端依赖

Electron 启动时会调用当前环境中的 `python` 来拉起 `backend/app.py`，所以要先保证这个 `python` 能运行后端依赖：

```powershell
cd backend
python -m pip install -r requirements.txt
```

如果当前 `python` 不是你想用的解释器，可以显式指定：

```powershell
$env:PROVIEW_DESKTOP_PYTHON = "D:\path\to\python.exe"
```

### 2. 构建桌面版前端资源

```powershell
cd desktop
npm run build:frontend
```

这个脚本会：

- 在需要时自动安装 `frontend` 依赖
- 以桌面模式构建 `frontend/dist`
- 为桌面版注入默认 API 地址 `http://127.0.0.1:18765`

### 3. 启动 Electron

```powershell
cd desktop
npx electron .
```

启动后 Electron 会：

- 先显示启动页
- 自动启动本地 Flask 后端
- 对 `/api/health` 做健康检查
- 检查通过后加载 `frontend/dist/app.html`

## 打包桌面版

推荐使用仓库根目录新增的 `package-desktop.ps1` 作为本地调试完成后的统一打包入口。

### 推荐方式：使用根目录脚本

```powershell
.\package-desktop.ps1
```

这个脚本会按顺序执行：

- 环境检查
- 激活指定的 Conda 环境
- 构建桌面版前端
- 构建桌面版后端
- 校验打包用的脱敏 `.env`
- 调用 Electron 打包
- 检查 `desktop/release/` 下的产物
- 输出完整日志到 `logs/desktop-package/`

默认行为：

- 默认 Conda 环境名：`proview-ai`
- 默认 Windows 打包目标：`nsis`、`portable`
- 默认会同时构建前端、后端并执行最终打包

常见用法：

```powershell
# 使用默认配置打包
.\package-desktop.ps1

# 指定 Conda 环境
.\package-desktop.ps1 -CondaEnvName my-env

# 只重新打包，不重复构建
.\package-desktop.ps1 -SkipFrontend -SkipBackend

# 只构建前后端，不执行最终打包
.\package-desktop.ps1 -SkipPackage
```

产物与日志位置：

- 打包产物：`desktop/release/`
- 打包日志：`logs/desktop-package/`

### 底层方式：直接调用 desktop 脚本

如果你只想直接调用 `desktop/` 下已有脚本，也可以继续使用：

打包 Windows 安装包与便携版：

```powershell
cd desktop
npm run dist
```

输出目录：

- `desktop/release/`

如果你只想生成未安装的目录包：

```powershell
cd desktop
npm run pack
```

打包过程会自动：

- 构建桌面版前端
- 用 PyInstaller 打包后端
- 用 `electron-builder` 生成 Windows 安装包和 portable 包

注意：

- 根目录 `package-desktop.ps1` 额外做了 Conda 环境检查、日志归档、脱敏 `.env` 校验和产物检查，更适合作为日常本地打包入口。
- 首次打包时，如果缺少 PyInstaller，脚本会自动安装。
- 打包脚本会生成一个“去敏感信息”的后端 `.env`，不会把你的 API Key 一起打进安装包。
- 用户首次运行桌面版后，应通过运行时配置页填写实际的模型/OCR/语音配置。

## 数据与文件存储

本项目默认是本地优先。

Web 本地开发时，常见文件位置：

- 运行时配置：`backend/.env`
- 本地数据库：通常在 `backend/data/`
- 上传简历与生成文件：`backend/` 下的运行目录

桌面版运行时，常见文件位置：

- 运行时配置：Electron 用户数据目录下的 `backend-data/.env`
- SQLite 数据库：Electron 用户数据目录下的 `backend-data/data/`
- 后端日志：Electron 用户数据目录下的日志目录

## 推荐的开发顺序

如果你是第一次接手这个仓库，推荐按下面顺序理解和运行：

1. 先读 `frontend/`，确认业务页面与路由。
2. 再读 `backend/app.py`，确认接口与运行时配置。
3. 先跑 Web 开发模式，确认前后端联通。
4. 最后再跑 `desktop/`，确认桌面启动链路和打包流程。

## 补充说明

- 根目录旧文档里曾出现过“React”之类的历史描述，但当前实际前端是 Vue 3。
- 桌面端当前是 Windows-first，打包脚本默认面向 Windows 安装包与 portable 包。
- 如果桌面版提示找不到前端资源，优先检查是否已经在 `desktop/` 目录执行过 `npm run build:frontend`。

---

# 密钥配置指导-功能简介
## 写在功能简介前面
桌面版就是网页版的加了个壳子，本质上运行web端和桌面exe功能都是一样的。使用配置密钥和功能简介我就以web端为例。
在开发的过程中可以现在web端调试出你喜欢的样式后运行根目录的`package-desktop.ps1`脚本就会在`desktop/release`生成对应的可执行文件。
## web端启动前后端
## 启动后端
当你配置好环境之后（假设你已经配置好了全局的Python解释器，下同），在根目录打开终端输入：
```
cd backend
python app.py
```
出现类似的输出就是启动成功：
![[Pasted image 20260415022055.png]]
## 启动前端
第一次启动前端的时候，在根目录打开终端输入：
```
cd frontend
npm install（本命令只在初次初次初始化前端时使用）
npm run build
npm run dev
```
出现类似的输出就是启动成功：
![[Pasted image 20260415022840.png]]
点击` http://localhost:5173/`进入web页面

## 初始化配置密钥
进入页面点击应用设置。配置密钥
![[a34a74a26bdc69786975818666062ea.png]]
![[92477119f37d0c60e745d545b6f0add.png]]
![[3254ba8d88e69408c205b660fca4ab6.png]] 
### 密钥配置指导
DeepSeek API URL和token需要去官网购买，这里我们使用百度提供的免费文心一言、PaddleOCR、语音服务的API（每日提供的数量足够你完成多次面试练习）
#### 文心一言大模型 API获取方式
登录百度星河社区`https://aistudio.baidu.com/overview`完成实名认证：
![[b35fb4a1d85ddd0c136ff0576648402.png]]
![[e6da98d1e8ba5e54598a5651d16c2ee.png]]
![[dd5906b528b5a1a3981d4dab872adc3.png]]
复制对应的密钥即可
#### PaddleOCR API获取方式
登录百度星河社区`https://aistudio.baidu.com/overview`完成实名认证：
![[4834759d1a2534a8e0992130f4e5bbe.png]]
![[7763155a127dba1e1c9ae56555b822d.png]]![[7c5854ad6c8bdbe4e8ddfd16d8877b1.png]]
复制对应密钥即可
#### 百度语音 API获取方式
完成登录和实名认证`https://cloud.baidu.com/doc/AI_REFERENCE/s/Im3zhy4w6`读取AI接入指南进行配置
![[2d1dd3681f5008c54576049f0eb89c8.png]]

## 功能简介
### 面试配置
提供多种面试场景配置、多种面试音色可选
![[fa674dc496310c55a107fa5ab104938 2.png]]
开启面试，会根据输入的简历格式调用OCR进行解析
![[3ff3dc28d26c009ea2834f1e53740dc.png]]
### 面试房间
能够实现语音实时交互面试，语音转为文字实时纠错
![[0a82c5e7499172261340e2c1c226e84.png]]
灵活结束面试，随时随地可练习面试技能
![[902a0f37fd36e5e4ee891f4293ce96b.png]]
### 评估报告
面试结束生成评估报告，能够直观分析面试过程中的不足
![[cc8ee88dbf82050a13d88268752e583.png]]
### 简历优化
可以选择直接优化，也可以定制化优化方向
![[0c679cfb61e4cdb4cbcf34f121c2488.png]]![[92feec4be55fb5283840585c3a3115d.png]]
### 简历生成
内置简历多种模板，集简历生成-AI优化-输出为一体的功能
![[83192b99831554bba147f0ede46f79b.png]]
### 我的简历
集中化管理简历
![[6d4a134827b6039980ec97d89ff36ee.png]]
### 职业生涯规划指导（完善中）
能够生成长期跟踪的职业规划指导
![[a585649200fabd2a4aed52d6aba4c8d.png]]
