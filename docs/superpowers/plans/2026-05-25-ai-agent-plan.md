# AI 智能体桌宠 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform 3-state GIF desktop pet into an AI agent with chat, document analysis, web search via configurable OpenAI-compatible API.

**Architecture:** 5 new Python modules (settings, ai_client, tools, chat_window, settings_dialog) + PetBridge/QML/main.py updates. Chat UI in PyQt6 widgets. AI calls via `openai` library streaming + function calling.

**Tech Stack:** PyQt6 6.7.0, openai>=1.0.0, PyMuPDF>=1.23.0, tavily-python>=0.3

---

### Task 1: Update requirements.txt

**Files:**
- Modify: `requirements.txt`

- [ ] **Add dependencies**

```
PyQt6==6.7.0
pyinstaller==6.10.0
openai>=1.0.0
PyMuPDF>=1.23.0
```

- [ ] **Commit**

```
git add requirements.txt
git commit -m "chore: add AI agent dependencies (openai, PyMuPDF)"
```

---

### Task 2: Create settings.py

**Files:**
- Create: `settings.py`
- Create: `test_settings.py`

- [ ] **Write test_settings.py**

```python
import tempfile
from unittest.mock import patch


def test_load_returns_defaults_when_file_missing():
    with tempfile.TemporaryDirectory() as tmp:
        with patch('settings.SETTINGS_DIR', tmp):
            from settings import load, DEFAULT_SETTINGS
            result = load()
            assert result == DEFAULT_SETTINGS


def test_save_and_load_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        with patch('settings.SETTINGS_DIR', tmp):
            from settings import load, save
            config = {
                'api_endpoint': 'https://custom.com/v1',
                'api_key': 'sk-test',
                'model': 'gpt-4',
                'system_prompt': 'You are helpful.',
                'search_api_key': 'tavily-test',
            }
            save(config)
            loaded = load()
            assert loaded == config


def test_load_merges_defaults_for_missing_keys():
    with tempfile.TemporaryDirectory() as tmp:
        with patch('settings.SETTINGS_DIR', tmp):
            from settings import load, save, DEFAULT_SETTINGS
            save({'api_endpoint': 'http://local:8000/v1'})
            result = load()
            assert result['api_endpoint'] == 'http://local:8000/v1'
            assert result['api_key'] == DEFAULT_SETTINGS['api_key']
```

- [ ] **Run tests** → FAIL (no module)

Run: `python3 -m pytest test_settings.py -v`

- [ ] **Write settings.py**

```python
import json
import os

SETTINGS_DIR = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', '罗小黑桌宠')
SETTINGS_FILE = os.path.join(SETTINGS_DIR, 'settings.json')

DEFAULT_SETTINGS = {
    'api_endpoint': 'https://api.openai.com/v1',
    'api_key': '',
    'model': 'gpt-4o-mini',
    'system_prompt': '',
    'search_api_key': '',
}


def load() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    with open(SETTINGS_FILE) as f:
        data = json.load(f)
    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    return merged


def save(config: dict):
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(config, f, indent=2)
```

- [ ] **Run tests** → PASS

Run: `python3 -m pytest test_settings.py -v`

- [ ] **Commit**

```
git add settings.py test_settings.py
git commit -m "feat: add settings module for AI API config"
```

---

### Task 3: Create tools.py

**Files:**
- Create: `tools.py`
- Create: `test_tools.py`

- [ ] **Write test_tools.py**

```python
import os
import tempfile


def test_read_txt():
    from tools import read_document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('Hello world')
        path = f.name
    try:
        assert read_document(path) == 'Hello world'
    finally:
        os.unlink(path)


def test_encode_image_returns_data_url():
    from tools import encode_image
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        f.write(b'fake-image-data')
        path = f.name
    try:
        data = encode_image(path)
        assert data.startswith('data:image/png;base64,')
    finally:
        os.unlink(path)


def test_web_search_no_key():
    from tools import web_search
    result = web_search('hello', api_key='')
    assert 'not configured' in result
```

- [ ] **Run tests** → FAIL

Run: `python3 -m pytest test_tools.py -v`

- [ ] **Write tools.py**

```python
import base64
import os


def read_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.txt', '.md', '.csv', '.json', '.py', '.js', '.ts', '.html', '.css'):
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    elif ext == '.pdf':
        import fitz
        doc = fitz.open(path)
        text = ''.join(page.get_text() for page in doc)
        doc.close()
        return text
    else:
        return f'Unsupported file type: {ext}'


def encode_image(path: str) -> str:
    with open(path, 'rb') as f:
        data = f.read()
    ext = os.path.splitext(path)[1].lower().lstrip('.')
    mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'png': 'image/png', 'gif': 'image/gif',
            'webp': 'image/webp'}.get(ext, 'image/png')
    b64 = base64.b64encode(data).decode('ascii')
    return f'data:{mime};base64,{b64}'


def web_search(query: str, api_key: str = '') -> str:
    if not api_key:
        return 'Web search not configured (no API key).'
    try:
        from tavily import TavilyClient
    except ImportError:
        return 'Search library not available.'
    try:
        result = TavilyClient(api_key=api_key).search(query)
        snippets = [r.get('content', '') for r in result.get('results', [])]
        return '\n'.join(snippets) if snippets else 'No results found.'
    except Exception as e:
        return f'Search error: {e}'
```

- [ ] **Run tests** → PASS

Run: `python3 -m pytest test_tools.py -v`

- [ ] **Commit**

```
git add tools.py test_tools.py
git commit -m "feat: add tools for document reading, image encoding, web search"
```

---

### Task 4: Create ai_client.py

**Files:**
- Create: `ai_client.py`

- [ ] **Write ai_client.py**

```python
from openai import OpenAI
from tools import web_search


class AiClient:
    def __init__(self, config: dict):
        self.client = OpenAI(
            base_url=config['api_endpoint'],
            api_key=config['api_key'],
        )
        self.model = config['model']
        self.system_prompt = config['system_prompt']
        self.search_api_key = config.get('search_api_key', '')

    def _build_messages(self, history: list) -> list:
        messages = []
        if self.system_prompt:
            messages.append({'role': 'system', 'content': self.system_prompt})
        messages.extend(history)
        return messages

    def _get_tools(self) -> list:
        if self.search_api_key:
            return [{
                'type': 'function',
                'function': {
                    'name': 'web_search',
                    'description': 'Search the internet for current information',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {
                                'type': 'string',
                                'description': 'Search query',
                            }
                        },
                        'required': ['query'],
                    },
                },
            }]
        return []

    def stream_chat(self, history: list):
        messages = self._build_messages(history)
        tools = self._get_tools()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools if tools else None,
            stream=True,
        )
        tool_calls = {}
        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta is None:
                continue
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls:
                        tool_calls[idx] = {'name': '', 'args': ''}
                    if tc.function.name:
                        tool_calls[idx]['name'] += tc.function.name
                    if tc.function.arguments:
                        tool_calls[idx]['args'] += tc.function.arguments
            if delta.content:
                yield delta.content

        if tool_calls:
            import json
            history.append({'role': 'assistant', 'content': None,
                           'tool_calls': [{'id': f'call_{k}', 'type': 'function',
                                          'function': {'name': v['name'],
                                                       'arguments': v['args']}}
                                         for k, v in tool_calls.items()]})
            for idx, tc in tool_calls.items():
                name = tc['name']
                args = json.loads(tc['args'])
                if name == 'web_search':
                    result = web_search(args['query'], self.search_api_key)
                    history.append({
                        'role': 'tool',
                        'tool_call_id': f'call_{idx}',
                        'content': result,
                    })
            second_pass = self.client.chat.completions.create(
                model=self.model,
                messages=self._build_messages(history),
                stream=True,
            )
            for chunk in second_pass:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    yield delta.content
```

Note: ai_client.py is tested via manual integration (requires API key). No automated tests for network-dependent code.

- [ ] **Commit**

```
git add ai_client.py
git commit -m "feat: add AiClient with streaming chat and web search function calling"
```

---

### Task 5: Update PetBridge (renderer.py)

**Files:**
- Modify: `renderer.py`

- [ ] **Add new signals and properties**

```python
from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal


class PetBridge(QObject):
    stateChanged = pyqtSignal()
    clickRequested = pyqtSignal()
    dragMoveRequested = pyqtSignal(int, int)
    contextMenuRequested = pyqtSignal()
    filesDropped = pyqtSignal(list)
    chatRequested = pyqtSignal()
    thinkingChanged = pyqtSignal()
    bubbleTextChanged = pyqtSignal()

    def __init__(self, pet, parent=None):
        super().__init__(parent)
        self._pet = pet
        self._thinking = False
        self._bubble_text = ''

    def sync(self):
        self.stateChanged.emit()

    @pyqtProperty(str, notify=stateChanged)
    def petState(self) -> str:
        return self._pet.state if hasattr(self._pet, 'state') else 'idle'

    @pyqtProperty(bool, notify=thinkingChanged)
    def petThinking(self) -> bool:
        return self._thinking

    @petThinking.setter
    def petThinking(self, val: bool):
        if self._thinking != val:
            self._thinking = val
            self.thinkingChanged.emit()

    @pyqtProperty(str, notify=bubbleTextChanged)
    def bubbleText(self) -> str:
        return self._bubble_text

    @bubbleText.setter
    def bubbleText(self, val: str):
        if self._bubble_text != val:
            self._bubble_text = val
            self.bubbleTextChanged.emit()
```

- [ ] **Run pet tests** → still PASS

Run: `python3 -m pytest test_pet.py -v`

- [ ] **Commit**

```
git add renderer.py
git commit -m "feat: add thinking, bubble, context menu, file drop signals to PetBridge"
```

---

### Task 6: Update PetPanel.qml

**Files:**
- Modify: `resources/ui/PetPanel.qml`

- [ ] **Rewrite PetPanel.qml with thinking animation, bubble, DropArea, right-click**

```qml
import QtQuick 2.15

Item {
    id: root
    width: parent ? parent.width : 120
    height: parent ? parent.height : 120
    clip: true

    property string petState: "idle"
    property bool petThinking: false
    property string bubbleText: ""

    function gifForState(state) {
        switch(state) {
            case 'idle': return gifBaseUrl + '待机.gif';
            case 'walk': return gifBaseUrl + '奔跑.gif';
            case 'angry': return gifBaseUrl + '疲惫.gif';
            default: return gifBaseUrl + '待机.gif';
        }
    }

    AnimatedImage {
        anchors.centerIn: parent
        width: 80; height: 80
        fillMode: Image.PreserveAspectFit
        smooth: true
        source: gifBaseUrl + '思考.gif'
        playing: petThinking
        visible: petThinking
    }

    AnimatedImage {
        anchors.centerIn: parent
        width: 80; height: 80
        fillMode: Image.PreserveAspectFit
        smooth: true
        source: gifForState(petState)
        playing: !petThinking
        visible: !petThinking
    }

    Rectangle {
        id: bubble
        anchors.horizontalCenter: parent.horizontalCenter
        y: -8
        padding: 8
        radius: 8
        color: "#ffffff"
        border.color: "#cccccc"
        border.width: 1
        visible: bubbleText !== ""
        opacity: bubbleText !== "" ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 150 } }

        Text {
            text: bubbleText
            font.pixelSize: 12
            color: "#333333"
        }
    }

    DropArea {
        anchors.fill: parent
        onEntered: {
            if (drag.hasUrls) {
                drag.accept()
                petBridge.petThinking = true
                petBridge.bubbleText = "给我的？"
            }
        }
        onExited: {
            petBridge.petThinking = false
            petBridge.bubbleText = ""
        }
        onDropped: {
            if (drop.hasUrls) {
                var paths = []
                for (var i = 0; i < drop.urls.length; i++) {
                    paths.push(drop.urls[i].toString())
                }
                petBridge.filesDropped(paths)
                drop.accept()
            }
            petBridge.petThinking = false
            petBridge.bubbleText = ""
            petBridge.chatRequested()
        }
    }

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton

        property int dragStartX: 0
        property int dragStartY: 0
        property bool wasDragged: false

        onPressed: function(mouse) {
            if (mouse.button !== Qt.LeftButton) return
            dragStartX = mouse.x
            dragStartY = mouse.y
            wasDragged = false
        }

        onPositionChanged: function(mouse) {
            if (mouse.button !== Qt.LeftButton) return
            var dx = mouse.x - dragStartX
            var dy = mouse.y - dragStartY
            if (Math.abs(dx) + Math.abs(dy) > 5) {
                wasDragged = true
                petBridge.dragMoveRequested(dx, dy)
                dragStartX = mouse.x
                dragStartY = mouse.y
            }
        }

        onReleased: function(mouse) {
            if (mouse.button !== Qt.LeftButton) return
            if (!wasDragged) {
                petBridge.clickRequested()
            }
        }

        onClicked: function(mouse) {
            if (mouse.button === Qt.RightButton) {
                petBridge.contextMenuRequested()
            }
        }
    }
}
```

- [ ] **Commit**

```
git add resources/ui/PetPanel.qml
git commit -m "feat: add thinking GIF, bubble, DropArea, right-click to PetPanel"
```

---

### Task 7: Create chat_window.py

**Files:**
- Create: `chat_window.py`

- [ ] **Write chat_window.py**

```python
import os
import threading
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QTextEdit, QPushButton, QLabel, QFrame, QFileDialog,
    QComboBox, QSizePolicy,
)
from ai_client import AiClient
from tools import read_document, encode_image


class MessageBubble(QFrame):
    def __init__(self, text, is_user=False):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        label = QLabel(text if text else '')
        label.setWordWrap(True)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label)
        self.setMaximumWidth(400)


class ChatWindow(QWidget):
    def __init__(self, ai_client=None):
        super().__init__()
        self._ai_client = ai_client
        self._messages = []
        self._stream_buffer = ''
        self._current_bubble = None
        self.setWindowTitle('罗小黑聊天')
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.resize(480, 600)
        self._setup_ui()

    def set_ai_client(self, client):
        self._ai_client = client

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_widget = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_widget)
        self._scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._scroll_widget)
        layout.addWidget(self._scroll)

        input_layout = QHBoxLayout()
        self._input = QTextEdit()
        self._input.setMaximumHeight(80)
        self._input.setPlaceholderText('输入消息...')
        self._input.setAcceptRichText(False)
        input_layout.addWidget(self._input)

        self._send_btn = QPushButton('发送')
        self._send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self._send_btn)

        self._file_btn = QPushButton('📎')
        self._file_btn.clicked.connect(self._on_upload_file)
        input_layout.addWidget(self._file_btn)

        layout.addLayout(input_layout)

    def add_message(self, text, is_user=False):
        bubble = MessageBubble(text, is_user)
        self._scroll_layout.addWidget(bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        scrollbar = self._scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_send(self):
        text = self._input.toPlainText().strip()
        if not text:
            return
        self._input.clear()
        self._send_message(text)

    def _send_message(self, text, file_context=None):
        if not self._ai_client:
            self.add_message('请先在 API 配置中设置模型', is_user=False)
            return

        content = [{'type': 'text', 'text': text}]
        if file_context:
            content.insert(0, {'type': 'text', 'text': file_context})
        self._messages.append({'role': 'user', 'content': content})
        self.add_message(text, is_user=True)

        self._current_bubble = MessageBubble('')
        self._scroll_layout.addWidget(self._current_bubble)
        self._stream_buffer = ''

        def stream():
            try:
                for chunk in self._ai_client.stream_chat(self._messages):
                    self._stream_buffer += chunk
                    QTimer.singleShot(0, self._update_stream)
            except Exception as e:
                self._stream_buffer = f'[Error] {e}'
                QTimer.singleShot(0, self._update_stream)

        t = threading.Thread(target=stream, daemon=True)
        t.start()

    def _update_stream(self):
        if self._current_bubble:
            label = self._current_bubble.findChild(QLabel)
            if label:
                label.setText(self._stream_buffer)
            self._scroll_to_bottom()
        if not self._stream_buffer.startswith('[Error]'):
            # After streaming completes, save assistant message
            # We detect completion by checking if thread is still alive
            pass

    def _on_upload_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, '选择文件', '',
            'All Files (*)')
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
            data_url = encode_image(path)
            content = [{'type': 'text', 'text': '分析这张图片'},
                       {'type': 'image_url',
                        'image_url': {'url': data_url}}]
            self._messages.append({'role': 'user', 'content': content})
            self.add_message(f'[图片] {os.path.basename(path)}', is_user=True)
            self._send_message('分析这张图片')
        else:
            text = read_document(path)
            preview = text[:2000]
            context = f'以下为文件 {os.path.basename(path)} 的内容:\n{preview}'
            self._send_message(f'分析文件: {os.path.basename(path)}',
                              file_context=context)

    def open_with_file(self, paths: list):
        self.show()
        self.raise_()
        for path in paths:
            ext = os.path.splitext(path)[1].lower()
            if ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
                data_url = encode_image(path)
                content = [{'type': 'text', 'text': '分析这张图片'},
                           {'type': 'image_url',
                            'image_url': {'url': data_url}}]
                self._messages.append({'role': 'user', 'content': content})
                self.add_message(f'[图片] {os.path.basename(path)}', is_user=True)
                self._send_message('分析这张图片')
            else:
                text = read_document(path)
                preview = text[:2000]
                context = f'以下为文件 {os.path.basename(path)} 的内容:\n{preview}'
                self._send_message(f'分析文件: {os.path.basename(path)}',
                                  file_context=context)
```

- [ ] **Commit**

```
git add chat_window.py
git commit -m "feat: add ChatWindow with streaming AI chat and file upload"
```

---

### Task 8: Create settings_dialog.py

**Files:**
- Create: `settings_dialog.py`

- [ ] **Write settings_dialog.py**

```python
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPlainTextEdit, QPushButton, QDialogButtonBox, QMessageBox,
)
from settings import load, save


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('API 配置')
        self.resize(480, 400)
        self._config = load()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._endpoint = QLineEdit(self._config['api_endpoint'])
        form.addRow('API Endpoint:', self._endpoint)

        self._api_key = QLineEdit(self._config['api_key'])
        self._api_key.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow('API Key:', self._api_key)

        self._model = QLineEdit(self._config['model'])
        form.addRow('Model:', self._model)

        self._system_prompt = QPlainTextEdit(self._config['system_prompt'])
        self._system_prompt.setPlaceholderText('可选：设置 AI 的系统提示词')
        form.addRow('System Prompt:', self._system_prompt)

        self._search_key = QLineEdit(self._config['search_api_key'])
        self._search_key.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow('Search API Key (Tavily):', self._search_key)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_save(self):
        config = {
            'api_endpoint': self._endpoint.text().strip(),
            'api_key': self._api_key.text().strip(),
            'model': self._model.text().strip(),
            'system_prompt': self._system_prompt.toPlainText().strip(),
            'search_api_key': self._search_key.text().strip(),
        }
        if not config['api_endpoint']:
            QMessageBox.warning(self, '错误', 'API Endpoint 不能为空')
            return
        if not config['api_key']:
            QMessageBox.warning(self, '错误', 'API Key 不能为空')
            return
        save(config)
        self._config = config
        self.accept()

    @property
    def config(self) -> dict:
        return self._config
```

- [ ] **Commit**

```
git add settings_dialog.py
git commit -m "feat: add SettingsDialog for AI API configuration"
```

---

### Task 9: Update main.py

**Files:**
- Modify: `main.py`

- [ ] **Add imports, new module init, signal connections, context menu, singleton chat window**

Changes to `main.py`:
1. Import new modules
2. Create AiClient, load settings
3. Create ChatWindow singleton
4. Connect new PetBridge signals
5. Handle right-click context menu
6. Refresh AiClient after settings change

```python
import os
import sys
from PyQt6.QtCore import QTimer, Qt, QUrl
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMenu, QWidget, QVBoxLayout,
    QSystemTrayIcon,
)
from PyQt6.QtQuickWidgets import QQuickWidget

from pet import Pet
from renderer import PetBridge
from settings import load as load_settings, save as save_settings
from ai_client import AiClient
from chat_window import ChatWindow
from settings_dialog import SettingsDialog


WINDOW_SIZE = 120


def _get_sprite_dir():
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'resources', 'sprites')


class DesktopPetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('罗小黑桌宠')
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)
        self.move_to_bottom_center()

        self.pet = Pet()
        self._settings = load_settings()
        self._ai_client = AiClient(self._settings)
        self._chat_window = ChatWindow(self._ai_client)

        sprite_dir = _get_sprite_dir()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.bridge = PetBridge(self.pet)
        self.qml_widget = QQuickWidget()
        self.qml_widget.setClearColor(Qt.GlobalColor.transparent)
        self.qml_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        root_context = self.qml_widget.rootContext()
        root_context.setContextProperty('petBridge', self.bridge)
        gif_url = QUrl.fromLocalFile(sprite_dir + '/').toString()
        root_context.setContextProperty('gifBaseUrl', gif_url)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        qml_path = os.path.join(base_path, 'resources/ui/PetPanel.qml')
        self.qml_widget.setSource(QUrl.fromLocalFile(qml_path))
        self.qml_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        layout.addWidget(self.qml_widget)

        self.bridge.stateChanged.connect(self._update_qml_state)
        self.bridge.clickRequested.connect(self.pet.on_click)
        self.bridge.dragMoveRequested.connect(self._on_drag_move)
        self.bridge.contextMenuRequested.connect(self._show_context_menu)
        self.bridge.filesDropped.connect(self._on_files_dropped)
        self.bridge.chatRequested.connect(self._open_chat)

        self.timer = QTimer()
        self.timer.timeout.connect(self._game_loop)
        self.timer.start(33)

        self._setup_tray()

    def _update_qml_state(self):
        root = self.qml_widget.rootObject()
        if root:
            root.setProperty('petState', self.pet.state)

    def _game_loop(self):
        self.pet.update(33)
        self.bridge.sync()

    def _on_drag_move(self, dx, dy):
        self.move(self.x() + dx, self.y() + dy)

    def _show_context_menu(self):
        menu = QMenu(self)
        chat_action = menu.addAction('💬 聊天')
        chat_action.triggered.connect(self._open_chat)
        settings_action = menu.addAction('⚙️ API 配置')
        settings_action.triggered.connect(self._open_settings)
        menu.addSeparator()
        quit_action = menu.addAction('🚪 退出')
        quit_action.triggered.connect(QApplication.quit)
        menu.exec(QCursor.pos())

    def _open_chat(self):
        self._chat_window.show()
        self._chat_window.raise_()
        self._chat_window.activateWindow()

    def _on_files_dropped(self, paths):
        self._open_chat()
        self._chat_window.open_with_file(paths)

    def _open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self._settings = dialog.config
            self._ai_client = AiClient(self._settings)
            self._chat_window.set_ai_client(self._ai_client)

    def move_to_bottom_center(self):
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.left() + (geometry.width() - WINDOW_SIZE) // 2
            y = geometry.bottom() - WINDOW_SIZE
            self.move(x, y)

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.black)
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.show()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('罗小黑桌宠')
    window = DesktopPetWindow()
    window.show()
    QTimer.singleShot(100, lambda: window.qml_widget.quickWindow().setColor(Qt.GlobalColor.transparent))
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
```

Wait, I need `from PyQt6.QtGui import QCursor`. Let me add that.

Also I need `from PyQt6.QtCore import Qt` which is already imported.

- [ ] **Run tests** → all PASS

Run: `python3 -m pytest test_pet.py test_settings.py test_tools.py -v`

- [ ] **Commit**

```
git add main.py
git commit -m "feat: integrate AI chat, settings, right-click menu, file drop into main"
```

---

### Task 10: Add thinking.gif to sprites

**Files:**
- Add: `resources/sprites/思考.gif`

- [ ] **Place thinking.gif in sprites directory**

The user provides the file. Place it at `resources/sprites/思考.gif`.

- [ ] **Commit**

```
git add resources/sprites/思考.gif
git commit -m "feat: add thinking animation sprite"
```

---

### Task 11: Update build.spec

**Files:**
- Modify: `build.spec`

- [ ] **Add hidden imports for new dependencies**

```python
from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/ui/PetPanel.qml', 'resources/ui'),
        ('resources/sprites', 'resources/sprites'),
    ],
    hiddenimports=[
        'PyQt6.QtQml',
        'PyQt6.QtQuick',
        'PyQt6.QtNetwork',
        'openai',
        'httpx',
        'fitz',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest',
    ],
    noarchive=False,
)
```

- [ ] **Build and verify**

Run: `rm -rf dist/ build/ && python3 -m PyInstaller build.spec --clean`
Expected: BUILD SUCCESSFUL

- [ ] **Commit**

```
git add build.spec
git commit -m "chore: update build.spec with AI agent hidden imports"
```

---

### Task 12: Install deps and run final integration check

- [ ] **Install dependencies**

Run: `pip install openai PyMuPDF`

- [ ] **Run all tests**

Run: `python3 -m pytest test_pet.py test_settings.py test_tools.py -v`
Expected: All PASS

- [ ] **Full build from clean**

Run: `rm -rf dist/ build/ && python3 -m PyInstaller build.spec --clean`

- [ ] **Final commit**

```
git commit -m "chore: finalize AI agent implementation"
```

---

## File Change Summary

| File | Action | Purpose |
|------|--------|---------|
| `requirements.txt` | Modify | Add openai, PyMuPDF |
| `settings.py` | Create | Config persistence |
| `test_settings.py` | Create | Settings tests |
| `tools.py` | Create | Document read, image encode, web search |
| `test_tools.py` | Create | Tools tests |
| `ai_client.py` | Create | OpenAI API client with streaming + function calling |
| `renderer.py` | Modify | Add thinking, bubble, context menu, file drop signals |
| `resources/ui/PetPanel.qml` | Modify | Add thinking GIF, bubble, DropArea, right-click |
| `chat_window.py` | Create | Chat UI with streaming, file upload |
| `settings_dialog.py` | Create | API config form |
| `main.py` | Modify | Integrate all new modules |
| `resources/sprites/思考.gif` | Add | Thinking animation (user provides) |
| `build.spec` | Modify | Add hidden imports |
