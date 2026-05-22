import math
import random
import time


class Pet:
    STATES = {
        'idle': 'idle',
        'walk': 'walk',
        'jump': 'jump',
        'sleep': 'sleep',
        'chase': 'chase',
        'drag': 'drag',
        'hang': 'hang',
    }

    SPEED_WALK = 50
    SPEED_CHASE = 80
    WALK_DURATION = (2000, 5000)
    SLEEP_TIMEOUT = 15000
    JUMP_DURATION = 600
    HANG_DURATION = 2000
    BOUNDARY_MARGIN = 20
    CHASE_DISTANCE = 100
    CLICK_RADIUS = 50

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.vx = 0.0
        self.vy = 0.0
        self.facing_right = True
        self.state = 'idle'
        self.state_timer = 0.0
        self.state_duration = 0.0
        self.idle_timer = 0.0
        self.speech_text = ''
        self.speech_timer = 0.0
        self.mouse_x = 0
        self.last_interaction_time = time.time() * 1000

    def update(self, dt: float):
        self.state_timer += dt
        self.idle_timer += dt
        self.speech_timer = max(0, self.speech_timer - dt)

        self.x += self.vx * (dt / 1000)
        self.y += self.vy * (dt / 1000)
        self._clamp_position()

        if self.state_duration > 0 and self.state_timer >= self.state_duration:
            self._transition_from(self.state)

        if self.state != 'sleep' and self.state != 'drag':
            now = time.time() * 1000
            if now - self.last_interaction_time > self.SLEEP_TIMEOUT:
                self.state = 'sleep'
                self.state_timer = 0
                self.state_duration = 0
                self.vx = 0
                self.vy = 0

    def _clamp_position(self):
        m = self.BOUNDARY_MARGIN
        if self.x < m:
            self.x = m
            self.vx = abs(self.vx)
            self.facing_right = True
        elif self.x > self.screen_width - m:
            self.x = self.screen_width - m
            self.vx = -abs(self.vx)
            self.facing_right = False
        if self.y < m:
            self.y = m
            self.vy = abs(self.vy)
        elif self.y > self.screen_height - m:
            self.y = self.screen_height - m
            self.vy = -abs(self.vy)

    def _transition_from(self, state: str):
        if state == 'walk':
            self._set_state('idle', 3000 + random.random() * 3000)
        elif state == 'jump':
            self._set_state('idle', 2000 + random.random() * 3000)
        elif state == 'hang':
            self._set_state('idle', 2000)
        elif state == 'idle':
            r = random.random()
            if r < 0.3:
                self._start_walk()
            else:
                self._set_state('idle', 2000 + random.random() * 3000)

    def _start_walk(self):
        angle = random.random() * math.pi * 2
        self.vx = math.cos(angle) * self.SPEED_WALK
        self.vy = math.sin(angle) * self.SPEED_WALK
        self.facing_right = self.vx >= 0
        duration = random.uniform(*self.WALK_DURATION)
        self._set_state('walk', duration)

    def _set_state(self, state: str, duration: float = 0):
        self.state = state
        self.state_timer = 0
        self.state_duration = duration
        if state != 'walk':
            self.vx = 0
            self.vy = 0

    def on_click(self):
        if self.state == 'sleep':
            self._set_state('jump', self.JUMP_DURATION)
            self._show_speech('！？')
            return
        self._set_state('jump', self.JUMP_DURATION)
        self._show_speech(random.choice(['呜？', '干嘛~', '嗯？']))
        self.last_interaction_time = time.time() * 1000

    def on_double_click(self):
        self._set_state('jump', self.JUMP_DURATION)
        self._show_speech(random.choice(['主人！❤️', '嘿！']))
        self.last_interaction_time = time.time() * 1000

    def on_drag_start(self):
        self.state = 'drag'
        self.state_timer = 0
        self.state_duration = 0
        self.vx = 0
        self.vy = 0
        self._show_speech(random.choice(['诶诶诶！', '放开我！']))

    def on_drag_move(self, x: float, y: float):
        self.x = x
        self.y = y
        self.state = 'drag'
        self.state_timer = 0

    def on_drag_end(self, x: float, y: float):
        self.x = x
        self.y = y
        if (x < self.BOUNDARY_MARGIN or
            x > self.screen_width - self.BOUNDARY_MARGIN or
            y < self.BOUNDARY_MARGIN or
            y > self.screen_height - self.BOUNDARY_MARGIN):
            self._set_state('hang', self.HANG_DURATION)
            self._show_speech(random.choice(['救命！', '好高！']))
        else:
            self._set_state('idle', 2000)

    def on_mouse_near(self, dist: float, mouse_x: float):
        if self.state == 'drag' or self.state == 'sleep':
            return
        self.last_interaction_time = time.time() * 1000
        if dist < self.CHASE_DISTANCE and self.state != 'chase':
            self.state = 'chase'
            self.state_timer = 0
            self.state_duration = 0
        self.facing_right = mouse_x > self.x

    def update_chase_target(self, mouse_x: float, mouse_y: float):
        if self.state != 'chase':
            return
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.CHASE_DISTANCE:
            self.vx = 0
            self.vy = 0
            self._set_state('idle', 2000)
            return
        if dist > 5:
            self.vx = (dx / dist) * self.SPEED_CHASE
            self.vy = (dy / dist) * self.SPEED_CHASE
            self.facing_right = dx > 0
        else:
            self.vx = 0
            self.vy = 0
            self._set_state('idle', 2000)

    def wake_up(self):
        if self.state == 'sleep':
            self._set_state('jump', 400)
            self._show_speech('！？')

    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        self.x = min(self.x, width - self.BOUNDARY_MARGIN)
        self.y = min(self.y, height - self.BOUNDARY_MARGIN)

    def _show_speech(self, text: str):
        self.speech_text = text
        self.speech_timer = 2000.0

    def get_speech(self) -> str:
        if self.speech_timer > 0:
            return self.speech_text
        return ''

    def get_position(self) -> tuple:
        return (self.x, self.y)
