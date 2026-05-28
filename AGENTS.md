# OpenCode Agent Guide for 罗小黑桌宠

## 🚀 Core Commands
- Run app: `python3 main.py`
- Run all tests: `python3 -m pytest`
- Build .app: `pyinstaller build.spec`
- Update planning skill: `npx skills update planning-with-files`

## 🔧 Development Notes
- **Entry point**: `main.py` → `DesktopPetWindow` (120x120 frameless QWidget)
- **Pet states**: idle ↔ walk → angry (10 min timer or click cycles)
- **File drop**: Triggers thinking animation → auto-opens chat for analysis
- **Right-click menu**: 聊天 / API 配置 / 退出
- **Chat window**: Streaming responses, bubble height auto-adjusts via QFontMetrics
- **Settings**: Stored in `~/Library/Application Support/罗小黑桌宠/settings.json`
- **Rendering**: SpritePlayer (QOpenGLWidget + PNG sprite sequences), pet thinking vs state frames auto-swapped

## 📦 Build Specifics
- Framework: PySide6 (not PyQt6)
- Hidden imports: `openai`, `httpx`, `fitz` (PyMuPDF)
- Resources bundled: `resources/sprites/`
- No QML dependency
- **Sprite directory structure**: `resources/sprites/{state}.png/` directories, each containing numbered PNG frame files

## 🧪 Testing
- Unit tests: `test_*.py` (run individually or together)
- Pet state machine: `test_pet.py`
- Document tools: `test_tools.py`
- Settings: `test_settings.py`
- Chat window: `test_chat_window.py` (includes bubble height logic)

## 💡 Planning Assistance
- `planning-with-files` skill is installed (use `/plan:start` to begin)
- Creates persistent `task_plan.md`, `findings.md`, `progress.md`
- Prevents goal drift during long coding sessions