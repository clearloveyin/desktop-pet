import os
import sys
from PyQt6.QtCore import QTimer, Qt, QUrl
from PyQt6.QtGui import QAction, QIcon, QPixmap, QCursor
from PyQt6.QtWidgets import QApplication, QMenu, QWidget, QVBoxLayout, QSystemTrayIcon
from PyQt6.QtQuickWidgets import QQuickWidget

from pet import Pet
from renderer import PetBridge
from settings import load as load_settings
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
        # KNOWN ISSUE: macOS Metal renderer doesn't clear the transparent window
        # buffer between frames, causing persistent outline of first rendered
        # image. See docs/macos-transparency-bug.md for details.
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
    QTimer.singleShot(100, lambda: window.qml_widget.quickWindow().setColor(Qt.GlobalColor.transparent))
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
