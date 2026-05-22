import os
import sys
from PyQt6.QtCore import QTimer, Qt, QUrl
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QWidget, QVBoxLayout, QSystemTrayIcon
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtQml import QQmlContext

from pet import Pet
from renderer import PetBridge


WINDOW_SIZE = 120


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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.qml_widget = QQuickWidget()
        self.qml_widget.setClearColor(Qt.GlobalColor.transparent)
        self.qml_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        qml_path = os.path.join(base_path, 'resources/ui/PetPanel.qml')
        self.qml_widget.setSource(QUrl.fromLocalFile(qml_path))
        self.qml_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        layout.addWidget(self.qml_widget)

        self.bridge = PetBridge(self.pet)
        root_context = self.qml_widget.rootContext()
        root_context.setContextProperty('petBridge', self.bridge)

        self.bridge.stateChanged.connect(self._update_qml_state)
        self.bridge.clickRequested.connect(self.pet.on_click)

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
