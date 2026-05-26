# AI 智能体桌宠 — 设计文档

## 概述

将现有的 3 态 GIF 桌宠（罗小黑）升级为 AI 智能体：支持自定义 OpenAI 兼容 API、对话聊天、文档分析、联网搜索。

## 交互设计

| 操作 | 行为 |
|------|------|
| **左键单击**（非拖拽） | 前进宠物状态：idle → walk → angry → idle 循环 |
| **左键拖拽** | 移动宠物窗口 |
| **右键单击** | 弹出右键菜单：聊天 / API 配置 / 退出 |
| **拖放文件到宠物身上** | 宠物显示思考动图 + 气泡"给我的？"，松开后自动打开聊天窗口分析文件 |

## 架构

```
QApplication
  └── DesktopPetWindow (QWidget, 120x120)
        ├── QQuickWidget (PetPanel.qml)
        │     ├── AnimatedImage ×3 (idle/walk/angry) — 按 petState 切换 visibility
        │     ├── AnimatedImage ×1 (thinking) — 按 petThinking 控制
        │     ├── DropArea — 文件拖放
        │     └── MouseArea — 左键单击/拖拽/右键菜单
        ├── Pet (state machine)
        ├── PetBridge (QObject → QML)
        ├── QTimer (33ms game loop)
        ├── QSystemTrayIcon
        └── ...新增:
              ├── AiClient — OpenAI 兼容 API 调用
              ├── ToolRegistry — 搜索 + 文档解析 + 图片编码
              ├── ChatWindow (QWidget) — 对话窗口
              └── SettingsDialog (QDialog) — API 配置

独立文件:
  settings.json — ~/Library/Application Support/罗小黑桌宠/settings.json
```

## 模块设计

### 1. PetBridge 新增接口

```
属性:
  petThinking: bool        — QML 控制显示思考动画
  bubbleText: string       — QML 聊天气泡文字

信号:
  contextMenuRequested()    — 右键 → Python 弹出菜单
  filesDropped(urls: list)  — 拖放文件 → Python 处理
  chatRequested()           — 打开聊天窗口
```

### 2. settings.py

```
文件: settings.json
字段:
  api_endpoint: str       — 例如 https://api.openai.com/v1
  api_key: str
  model: str              — 例如 gpt-4o-mini
  system_prompt: str      — 可选
  search_api_key: str     — Tavily API key，可选

接口:
  load() -> dict
  save(config: dict)
```

### 3. ai_client.py

```
class AiClient:
  def __init__(self, config: dict)
  def stream_chat(messages, tools=None) -> Generator[str]
    支持 streaming 返回 text delta
    支持 function calling（目前仅 search）
```

OpenAI 库原生支持 streaming 和 function calling。使用 `openai` Python 库，兼容任意 OpenAI 格式 API（含 vLLM、Ollama 等）。

### 4. tools.py

```
class ToolRegistry:
  def web_search(query: str) -> str
    通过 Tavily API 搜索，返回摘要文本

  def read_document(path: str) -> str
    PDF → PyMuPDF 提取文本
    TXT/MD → 直接读取

  def encode_image(path: str) -> str
    返回 base64 data URL，用于多模态 API
```

搜索作为 function calling 集成到 AiClient 中。AI 模型自行判断何时调用搜索。

### 5. chat_window.py

PyQt6 QWidget 窗口，**单例模式**（重复请求时聚焦已有窗口而非新建），包含:
- 顶部: 模型名称下拉框
- 中部: QScrollArea + QVBoxLayout，每条消息为一个 QFrame（用户/AI 区分样式），AI 回复 streaming 时逐字追加
- 底部: QTextEdit（输入）+ QPushButton（发送）+ QPushButton（上传文件）
- 通过 QThread 运行 AI 请求，emit 信号更新 UI

聊天消息结构（OpenAI 格式）:
```python
[
  {"role": "system", "content": system_prompt},
  {"role": "user", "content": [{"type": "text", "text": "..."}]},
  # 文件分析时 content 可能含 image_url
  {"role": "assistant", "content": "..."},
]
```

### 6. settings_dialog.py

PyQt6 QDialog 表单:
- API Endpoint (QLineEdit, placeholder: https://api.openai.com/v1)
- API Key (QLineEdit, echoMode: Password)
- Model (QLineEdit, placeholder: gpt-4o-mini)
- System Prompt (QPlainTextEdit, 可选)
- Search API Key (QLineEdit, 可选, placeholder: Tavily API key)
- [保存] [取消] 按钮

### 7. 文件拖放 → 聊天流程

```
1. 文件拖入 DropArea:
   → petThinking = true, bubbleText = "给我的？"
2. 文件在 DropArea 内松开:
   → filesDropped(urls) + chatRequested()
3. Python 打开 ChatWindow（如未打开）:
   → ToolRegistry 分析文件（PDF→文本 / 图片→base64）
   → 分析结果作为首条 user message
   → AiClient.stream_chat() → streaming 显示回复
4. 文件拖离 DropArea:
   → petThinking = false, bubbleText = ""
```

### 8. 右键菜单流程

```
1. QML MouseArea.onClicked (right button):
   → petBridge.contextMenuRequested()
2. Python DesktopPetWindow._show_context_menu():
   → QMenu: 聊天 / API 配置 / 退出
   → "聊天" → ChatWindow.open()
   → "API 配置" → SettingsDialog.exec()
   → "退出" → QApplication.quit()
```

## 新增依赖

```
openai>=1.0.0       # AI API 调用
PyMuPDF>=1.23.0     # PDF 文本提取
tavily-python>=0.3  # 联网搜索（可选，用户配 key 后才启用）
```

现有依赖不变: PyQt6==6.7.0, pyinstaller==6.10.0

## 构建说明

build.spec 需要新增:
- 将新模块的 Python 文件加入自动检测（PyInstaller 默认会追踪 import）
- settings_dialog.py / chat_window.py / ai_client.py / tools.py 会被 main.py 的 import 自动捕获
- 隐式导入: 可能需要添加 `openai`、`httpx`、`PyMuPDF` 等到 hiddenimports
- 数据文件: settings 无额外 bundle 需求

## 边界情况

- 网络请求超时: AiClient 使用 timeout 参数，超时后聊天窗口显示错误提示
- API key 无效: 返回 401 时提示用户检查配置
- 文件无法解析: ToolRegistry 返回错误信息，聊天窗口显示
- 搜索 API 未配置: AiClient 不注册 search function，搜索功能自动禁用
- 对话无历史: 每次关闭聊天窗口后清空 messages（用户确认不需要持久化）
- 思考 GIF 缺失: 若 sprites 目录无思考.gif，petThinking 回退到显示 idle
