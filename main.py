import os
import sys
import math
from PyQt6.QtCore import QTimer, Qt, QUrl
from PyQt6.QtGui import QAction, QGuiApplication, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QWidget, QVBoxLayout, QSystemTrayIcon
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtQml import QQmlContext

from pet import Pet
from renderer import PetBridge
from interaction import Interaction


class DesktopPetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('罗小黑桌宠')
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._setup_window_geometry()

        self.pet = Pet(self.width(), self.height())

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
        self.bridge.positionChanged.connect(self._update_qml_position)
        self.bridge.facingChanged.connect(self._update_qml_facing)
        self.bridge.bubbleChanged.connect(self._update_qml_bubble)

        self.interaction = Interaction(self.qml_widget, self.pet)

        self.last_time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._game_loop)
        self.timer.start(33)

        self._setup_tray()

    def _setup_window_geometry(self):
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            w = geometry.width()
            h = 200
            x = geometry.left()
            y = geometry.bottom() - h
            self.setGeometry(x, y, w, h)

    def _update_qml_state(self):
        root = self.qml_widget.rootObject()
        if root:
            root.setProperty('petState', self.pet.state)

    def _update_qml_position(self):
        root = self.qml_widget.rootObject()
        if root:
            root.setProperty('petX', self.pet.x)
            root.setProperty('petY', self.pet.y)

    def _update_qml_facing(self):
        root = self.qml_widget.rootObject()
        if root:
            root.setProperty('facingRight', self.pet.facing_right)

    def _update_qml_bubble(self):
        root = self.qml_widget.rootObject()
        if root:
            root.setProperty('bubbleText', self.bridge.bubbleText)
            root.setProperty('bubbleVisible', self.bridge.bubbleVisible)

    def _game_loop(self):
        self.pet.update(33)
        self.bridge.sync()

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
