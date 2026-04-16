# Tracking: 文件兼容性问题收集

## 背景

当前项目已经支持多种简历文件输入，但不同文件格式、来源软件、编码方式、扫描质量和运行环境仍可能导致解析失败、OCR 结果异常、预览异常或桌面端运行错误。

为了避免兼容性问题分散在多个 issue 中难以汇总，这个 issue 用来统一收集：

- 文件上传失败
- 文件类型识别失败
- OCR 解析失败或结果为空
- 文本提取结果异常
- 图片/附件提取异常
- 文件预览异常
- Web 与桌面端行为不一致

## 当前代码中的支持范围

### 已支持的简历扩展名

根据 [resume_text_extraction.py](../../backend/services/resume_text_extraction.py) 当前实现：

- OCR 路径：`.pdf`、`.jpg`、`.jpeg`、`.png`、`.bmp`、`.webp`、`.heic`、`.heif`
- 直接文本提取路径：`.docx`、`.md`、`.markdown`、`.txt`

### 当前明确不支持

- `.doc`
  - 当前会提示“暂不支持旧版 .doc，请先另存为 .docx 后再上传。”

### 当前实现里的兼容性关键点

根据 [ocr_processing.py](../../backend/core/tools/ocr_processing.py) 当前实现：

- `HEIC/HEIF` 会先尝试转换为 `PNG` 后再进入 OCR
- 图片文件进入 OCR 前可能经过预处理
- OCR 结果会落盘到本地 `ocr_outputs`
- 桌面端与 Web 端走的是同一套后端解析逻辑

## 已知问题

### 1. Windows 桌面端 OCR 日志编码问题

- 现象：
  - 上传 `PDF` 或图片时，桌面端在某些 Windows 环境下可能出现 `UnicodeEncodeError: 'gbk' codec can't encode character ...`
- 原因：
  - OCR 日志输出包含 emoji，而部分 Windows 控制台编码为 `gbk/cp936`
- 影响范围：
  - `PDF` 和图片都会受影响，因为都走 OCR 路径
- 当前状态：
  - 已在本地修复，等待验证更多用户环境

## 建议优先收集的兼容性维度

请尽量按下面维度补充案例，方便后续归类：

- 文件格式
  - `pdf` / `docx` / `txt` / `md` / `jpg` / `png` / `webp` / `heic` / `heif`
- 文件来源
  - WPS / Microsoft Word / Apple Pages 导出 / BOSS 直聘附件 / 招聘网站下载 / 手机相册 / 扫描件
- 文件特征
  - 文本型 PDF / 扫描型 PDF / 多页 PDF / 含图片 / 含表格 / 含特殊字符 / 超大文件 / 文件名含中文或空格
- 运行环境
  - Web / 桌面端
  - Windows / macOS / Linux
- 结果类型
  - 无法上传 / 无法识别格式 / OCR 报错 / 提取为空 / 文本乱码 / 预览错误 / 结果不完整

## 兼容性收集模板

后续在这个 issue 下追加案例时，建议按下面格式填写：

```md
### [文件格式] 简短标题

- 文件格式：
- 文件来源：
- 运行环境：
- 入口：
  - Web / 桌面端
- 文件特征：
  - 例如：扫描版 PDF / 双栏简历 / 含项目截图 / 文件名含中文
- 实际结果：
- 期望结果：
- 是否稳定复现：
  - 是 / 否 / 偶发
- 复现步骤：
  1.
  2.
  3.
- 报错信息或截图：
- 是否可提供脱敏样本：
  - 可以 / 不可以
```

## 建议的排查标签

如果后续要把这个 tracking issue 再拆子问题，可以优先按下面标签分类：

- `compat:file-type`
- `compat:ocr`
- `compat:docx`
- `compat:pdf`
- `compat:image`
- `compat:encoding`
- `compat:desktop`
- `compat:web`
- `compat:preview`

## 后续处理建议

- 先把用户反馈统一挂到这个 issue 下面，避免兼容性问题分散
- 当某一类问题累计到 2 到 3 个以上复现案例时，再拆独立 issue 处理
- 对于无法公开分享原始文件的案例，优先收集：
  - 导出来源
  - 页数
  - 文件大小
  - 是否扫描件
  - 是否包含表格/双栏/图片
  - 完整报错信息

## 初始检查清单

- [ ] Web 端 `PDF` 上传兼容性
- [ ] 桌面端 `PDF` 上传兼容性
- [ ] `DOCX` 文本提取兼容性
- [ ] `HEIC/HEIF` 转换兼容性
- [ ] 扫描型图片 OCR 兼容性
- [ ] 多页简历解析兼容性
- [ ] 文件名包含中文、空格、特殊字符的兼容性
- [ ] 超大文件与超时场景兼容性
- [ ] 解析失败时的用户提示是否足够明确

## 可直接用作 GitHub Issue 的标题

```md
Tracking: 文件兼容性问题收集（PDF / DOCX / 图片 / OCR / 桌面端）
```
