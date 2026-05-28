class Pet:
    STATE_CYCLE = ['idle', 'walk', 'angry']
    STATE_DURATION = 10 * 60 * 1000

    def __init__(self):
        self.state_index = 0
        self.state_timer = 0.0

    def update(self, dt):
        self.state_timer += dt
        if self.state_timer >= self.STATE_DURATION:
            self._next_state()

    def on_click(self):
        self._next_state()

    def _next_state(self):
        self.state_index = (self.state_index + 1) % 3
        self.state_timer = 0.0

    @property
    def state(self):
        return self.STATE_CYCLE[self.state_index]
