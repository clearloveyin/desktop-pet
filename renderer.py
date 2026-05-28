from PySide6.QtCore import QObject, Signal


class PetBridge(QObject):
    thinkingChanged = Signal()
    bubbleTextChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thinking = False
        self._bubble_text = ''

    @property
    def petThinking(self):
        return self._thinking

    @petThinking.setter
    def petThinking(self, val):
        if self._thinking != val:
            self._thinking = val
            self.thinkingChanged.emit()

    @property
    def bubbleText(self):
        return self._bubble_text

    @bubbleText.setter
    def bubbleText(self, val):
        if self._bubble_text != val:
            self._bubble_text = val
            self.bubbleTextChanged.emit()
