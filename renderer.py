from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal


class PetBridge(QObject):
    stateChanged = pyqtSignal()
    clickRequested = pyqtSignal()

    def __init__(self, pet, parent=None):
        super().__init__(parent)
        self._pet = pet

    def sync(self):
        self.stateChanged.emit()

    @pyqtProperty(str, notify=stateChanged)
    def petState(self) -> str:
        return self._pet.state if hasattr(self._pet, 'state') else 'idle'
