# 罗小黑桌宠 🐾

跨平台桌面宠物（macOS / Windows）—— 罗小黑，会 idle/walk/angry 三态切换，能聊天、分析文件。

## 功能

- 动画：待机 → 奔跑 → 疲惫，10 分钟自动循环 / 点击切换
- 聊天：右键菜单 → 聊天，流式回复
- 文件分析：拖入或点击 📎 上传文件（txt/md/csv/json/code/pdf）
- 托拽移动

## 前置要求

- Python 3.10+
- 依赖见 `requirements.txt`

## 安装 & 运行

```bash
pip install -r requirements.txt
```

| 平台 | 命令 |
|---|---|
| macOS / Linux | `python3 main.py` |
| Windows | `python main.py` |

## 首次使用

1. 右键 → API 配置
2. 填入 API Endpoint / Key / Model（支持任意 OpenAI 兼容接口）
3. 右键 → 聊天开始对话

## 构建可执行文件

```bash
pip install pyinstaller
pyinstaller build.spec
```

产物：`dist/罗小黑桌宠.app`（macOS）或 `dist/罗小黑桌宠.exe`（Windows）

## 项目结构

- `main.py` — 窗口、事件循环、拖放
- `pet.py` — 状态机 + 信号
- `sprite_player.py` — PNG 序列播放器
- `pet_view_model.py` — 思考/气泡状态
- `chat_window.py` — 聊天界面 + 流式
- `ai_client.py` — API 客户端
- `settings.py` — 配置持久化
  - macOS: `~/Library/Application Support/罗小黑桌宠/settings.json`
  - Windows: `%APPDATA%/罗小黑桌宠/settings.json`
- `tools.py` — 文档读取
- `settings_dialog.py` — API 配置弹窗

## 测试

```bash
python3 -m pytest
```

## 许可

MIT
