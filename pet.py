from PySide6.QtCore import QObject, Signal


class Pet(QObject):
    stateChanged = Signal(str)

    STATE_CYCLE = ['idle', 'walk', 'angry']
    STATE_DURATION = 10 * 60 * 1000

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state_index = 0
        self._state_timer = 0.0

    def update(self, dt):
        self._state_timer += dt
        if self._state_timer >= self.STATE_DURATION:
            self._next_state()

    def on_click(self):
        self._next_state()

    def _next_state(self):
        self._state_index = (self._state_index + 1) % 3
        self._state_timer = 0.0
        self.stateChanged.emit(self.state)

    @property
    def state(self):
        return self.STATE_CYCLE[self._state_index]
