from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal
from pet import Pet


class PetBridge(QObject):
    stateChanged = pyqtSignal()
    positionChanged = pyqtSignal()
    facingChanged = pyqtSignal()
    bubbleChanged = pyqtSignal()

    def __init__(self, pet: Pet, parent=None):
        super().__init__(parent)
        self._pet = pet
        self._bubble_text = ''
        self._bubble_visible = False

    def sync(self):
        self.stateChanged.emit()
        self.positionChanged.emit()
        self.facingChanged.emit()
        text = self._pet.get_speech()
        visible = len(text) > 0
        if text != self._bubble_text or visible != self._bubble_visible:
            self._bubble_text = text
            self._bubble_visible = visible
            self.bubbleChanged.emit()

    @pyqtProperty(str, notify=stateChanged)
    def petState(self) -> str:
        return self._pet.state if hasattr(self._pet, 'state') else 'idle'

    @pyqtProperty(float, notify=positionChanged)
    def petX(self) -> float:
        return self._pet.x if hasattr(self._pet, 'x') else 0

    @pyqtProperty(float, notify=positionChanged)
    def petY(self) -> float:
        return self._pet.y if hasattr(self._pet, 'y') else 0

    @pyqtProperty(bool, notify=facingChanged)
    def facingRight(self) -> bool:
        return self._pet.facing_right if hasattr(self._pet, 'facing_right') else True

    @pyqtProperty(str, notify=bubbleChanged)
    def bubbleText(self) -> str:
        return self._bubble_text

    @pyqtProperty(bool, notify=bubbleChanged)
    def bubbleVisible(self) -> bool:
        return self._bubble_visible
