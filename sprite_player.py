import os
import re
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QPixmap


class SpritePlayer(QObject):
    frameChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frames = []
        self._interval = 83
        self._index = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_frame)

    def load(self, dir_path, fps=12):
        self._timer.stop()
        self._frames.clear()
        self._index = 0
        self._interval = 1000 // fps
        files = [f for f in os.listdir(dir_path) if f.lower().endswith('.png')]
        files.sort(key=lambda n: int(re.findall(r'\d+', n)[-1]))
        for f in files:
            self._frames.append(QPixmap(os.path.join(dir_path, f)))
        if self._frames:
            self._timer.start(self._interval)
            self.frameChanged.emit()

    def _next_frame(self):
        if not self._frames:
            return
        self._index = (self._index + 1) % len(self._frames)
        self._timer.start(self._interval)
        self.frameChanged.emit()

    def current_pixmap(self):
        if self._frames:
            return self._frames[self._index]
        return QPixmap()
