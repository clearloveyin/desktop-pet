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
