import os
import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction, QIcon, QPixmap, QCursor, QPainter
from PySide6.QtWidgets import (
    QApplication, QMenu, QWidget, QSystemTrayIcon, QLabel
)

from pet import Pet
from sprite_player import SpritePlayer
from pet_view_model import PetBridge
from settings import Settings
from ai_client import AiClient
from chat_window import ChatWindow
from settings_dialog import SettingsDialog
from styles import MENU_STYLE


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
        self.setAcceptDrops(True)
        self.move_to_bottom_center()

        self.pet = Pet()
        self.pet.stateChanged.connect(self._on_pet_state_changed)
        self._settings = Settings.load()
        self._ai_client = AiClient(self._settings)
        self._chat_window = ChatWindow(self._ai_client)
        self._sprite_dir = _get_sprite_dir()

        self._bridge = PetBridge()
        self._bridge.thinkingChanged.connect(self._update_sprite)
        self._bridge.bubbleTextChanged.connect(self._update_bubble)

        self._current_sprite = ''
        self._pet_widget = SpritePlayer(self)
        self._pet_widget.frameChanged.connect(self.update)

        self._bubble_label = QLabel(self)
        self._bubble_label.setWordWrap(True)
        self._bubble_label.hide()
        self._bubble_label.setStyleSheet("""
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 8px;
            padding: 4px 8px;
            font-size: 12px;
            color: #333333;
        """)

        self._drag_start = None
        self._was_dragged = False

        self._update_sprite()

        self.timer = QTimer()
        self.timer.timeout.connect(self._game_loop)
        self.timer.start(33)

        self._setup_tray()

    def _sprite_path(self):
        if self._bridge.petThinking:
            return os.path.join(self._sprite_dir, '思考.png')
        state = self.pet.state
        mapping = {'idle': '待机.png', 'walk': '奔跑.png', 'angry': '疲惫.png'}
        return os.path.join(self._sprite_dir, mapping.get(state, '待机.png'))

    def _on_pet_state_changed(self, state):
        self._update_sprite()

    def _update_sprite(self):
        path = self._sprite_path()
        if path != self._current_sprite:
            self._current_sprite = path
            self._pet_widget.load(path, fps=12)

    def _update_bubble(self):
        text = self._bridge.bubbleText
        if text:
            self._bubble_label.setText(text)
            self._bubble_label.adjustSize()
            x = (WINDOW_SIZE - self._bubble_label.width()) // 2
            y = 2
            self._bubble_label.move(x, y)
            self._bubble_label.show()
        else:
            self._bubble_label.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceOver)
        pixmap = self._pet_widget.current_pixmap()
        if not pixmap.isNull():
            x = (self.width() - pixmap.width()) // 2
            y = (self.height() - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)
        painter.end()

    def _game_loop(self):
        self.pet.update(33)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position().toPoint()
            self._was_dragged = False

    def mouseMoveEvent(self, event):
        if self._drag_start and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.position().toPoint() - self._drag_start
            if delta.manhattanLength() > 5:
                self._was_dragged = True
                self.move(self.pos() + delta)
            self._drag_start = event.position().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._drag_start is not None:
            if not self._was_dragged:
                self.pet.on_click()
            self._drag_start = None

    def contextMenuEvent(self, event):
        self._show_context_menu()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._bridge.petThinking = True
            self._bridge.bubbleText = "给我的？"

    def dragLeaveEvent(self, event):
        self._bridge.petThinking = False
        self._bridge.bubbleText = ""

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self._bridge.petThinking = False
            self._bridge.bubbleText = ""
            self._on_files_dropped(paths)
            event.acceptProposedAction()

    def _show_context_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(MENU_STYLE)
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
        tray_menu = QMenu()
        quit_action = QAction('退出', self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('罗小黑桌宠')
    window = DesktopPetWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
