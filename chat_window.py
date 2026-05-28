import os
import threading
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QTextEdit, QPushButton, QLabel, QFrame, QFileDialog,
)
from ai_client import AiClient
from tools import read_document
from styles import CHAT_WINDOW_STYLE

MAX_BUBBLE_WIDTH = 400


class MessageBubble(QFrame):
    def __init__(self, text, is_user=False):
        super().__init__()
        self.setObjectName('UserBubble' if is_user else 'AiBubble')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        self.label = QLabel(text if text else '')
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(MAX_BUBBLE_WIDTH)
        font = QFont()
        font.setPixelSize(13)
        self.label.setFont(font)
        self.label.setStyleSheet('color: #3E5A3E;')
        layout.addWidget(self.label)
        self.setMaximumWidth(MAX_BUBBLE_WIDTH + 24)


class ChatWindow(QWidget):
    _update_requested = Signal()
    _done_requested = Signal()

    def __init__(self, ai_client=None):
        super().__init__()
        self.setObjectName('ChatWindow')
        self._ai_client = ai_client
        self._messages = []
        self._stream_buffer = ''
        self._current_bubble = None
        self.setWindowTitle('罗小黑聊天')
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.resize(480, 600)
        self._setup_ui()
        self.setStyleSheet(CHAT_WINDOW_STYLE)
        self._update_requested.connect(self._update_stream)
        self._done_requested.connect(self._on_stream_done)

    def set_ai_client(self, client):
        self._ai_client = client

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName('HeaderBar')
        header.setFixedHeight(40)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 0, 12, 0)
        title = QLabel('🐾 罗小黑聊天')
        title.setStyleSheet('color: #3E5A3E; font-size: 14px; font-weight: bold;')
        header_layout.addWidget(title)
        layout.addWidget(header)

        self._scroll = QScrollArea()
        self._scroll.setObjectName('ChatScroll')
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_widget = QWidget()
        self._scroll_widget.setObjectName('ScrollContainer')
        self._scroll_layout = QVBoxLayout(self._scroll_widget)
        self._scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll_layout.setContentsMargins(12, 8, 12, 8)
        self._scroll_layout.setSpacing(8)
        self._scroll.setWidget(self._scroll_widget)
        layout.addWidget(self._scroll, 1)

        # 创建输入容器 (视觉上作为输入框)
        input_container = QWidget()
        input_container.setObjectName('InputContainer')
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(12, 6, 12, 4)
        input_layout.setSpacing(0)

        self._input = QTextEdit()
        self._input.setObjectName('ChatInput')
        self._input.setPlaceholderText('输入消息...')
        self._input.setAcceptRichText(False)
        self._input.setMaximumHeight(48)
        input_layout.addWidget(self._input)

        # 底部按钮行 (在输入框内部右下角)
        bottom_row = QWidget()
        bottom_row.setObjectName('InputBottomRow')
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(6)

        bottom_layout.addStretch()

        self._file_btn = QPushButton('📎')
        self._file_btn.setObjectName('FileBtn')
        self._file_btn.setFixedSize(32, 32)
        self._file_btn.clicked.connect(self._on_upload_file)
        bottom_layout.addWidget(self._file_btn)

        self._send_btn = QPushButton('➡️')
        self._send_btn.setObjectName('SendBtn')
        self._send_btn.setFixedSize(28, 28)
        self._send_btn.clicked.connect(self._on_send)
        bottom_layout.addWidget(self._send_btn)

        input_layout.addWidget(bottom_row)
        layout.addWidget(input_container)

    def _update_bubble_height(self, bubble):
        """更新气泡高度以适应其内容"""
        label = bubble.label
        # 获取标签实际宽度（布局后）
        label_width = label.width()
        if label_width > 0:
            # 使用字体度量计算换行后的所需高度
            fm = label.fontMetrics()
            # 计算在给定宽度下文本的边界矩形
            rect = fm.boundingRect(
                0, 0, label_width, 2000,
                Qt.TextFlag.TextWordWrap | Qt.TextFlag.TextIncludeTrailingSpaces,
                label.text()
            )
            # 设置气泡最小高度（含边距）
            height = rect.height() + 16  # 8px 上边距 + 8px 下边距
            bubble.setMinimumHeight(height)
    
    def add_message(self, text, is_user=False):
        bubble = MessageBubble(text, is_user)
        align = Qt.AlignmentFlag.AlignRight if is_user else Qt.AlignmentFlag.AlignLeft
        self._scroll_layout.addWidget(bubble, 0, align)
        QTimer.singleShot(10, lambda: self._update_bubble_height(bubble))
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
        self._scroll_layout.addWidget(self._current_bubble, 0, Qt.AlignmentFlag.AlignLeft)
        self._stream_buffer = ''

        def stream():
            try:
                for chunk in self._ai_client.stream_chat(self._messages):
                    self._stream_buffer += chunk
                    self._update_requested.emit()
            except Exception as e:
                self._stream_buffer = f'[Error] {e}'
                self._update_requested.emit()
            self._done_requested.emit()

        t = threading.Thread(target=stream, daemon=True)
        t.start()

    def _on_stream_done(self):
        self._messages.append({'role': 'assistant', 'content': self._stream_buffer})

    def _update_stream(self):
        if self._current_bubble:
            self._current_bubble.label.setText(self._stream_buffer)
            QTimer.singleShot(0, lambda: self._update_bubble_height(self._current_bubble))
            self._scroll_to_bottom()

    def _on_upload_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, '选择文件', '',
            'All Files (*)')
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
            self.add_message(
                f'[图片] {os.path.basename(path)}（当前模型不支持图片分析）',
                is_user=True)
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
                self.add_message(
                    f'[图片] {os.path.basename(path)}（当前模型不支持图片分析）',
                    is_user=True)
            else:
                text = read_document(path)
                preview = text[:2000]
                context = f'以下为文件 {os.path.basename(path)} 的内容:\n{preview}'
                self._send_message(f'分析文件: {os.path.basename(path)}',
                                  file_context=context)
