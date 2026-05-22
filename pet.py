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

    WALK_SPEED = 17.5
    SPEED_CHASE = 80
    JUMP_DURATION = 600
    HANG_DURATION = 2000
    BOUNDARY_MARGIN = 20
    CHASE_DISTANCE = 100
    CLICK_RADIUS = 50

    WORK_DURATION = 30 * 60 * 1000
    REST_DURATION = 10 * 60 * 1000

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width // 2
        self.y = screen_height - 30
        self.vx = self.WALK_SPEED
        self.vy = 0.0
        self.facing_right = True
        self.state = 'walk'
        self.state_timer = 0.0
        self.state_duration = 0.0
        self.speech_text = ''
        self.speech_timer = 0.0

        self.work_timer = 0.0
        self.rest_timer = 0.0
        self.is_working = True

    def update(self, dt: float):
        self.state_timer += dt
        self.speech_timer = max(0, self.speech_timer - dt)

        if self.is_working:
            self.work_timer += dt
            if self.work_timer >= self.WORK_DURATION:
                self.is_working = False
                self.rest_timer = 0.0
                self._set_state('sleep')
        else:
            self.rest_timer += dt
            if self.rest_timer >= self.REST_DURATION:
                self.is_working = True
                self.work_timer = 0.0
                self._start_walk()

        self.x += self.vx * (dt / 1000)
        self._clamp_position()

        if self.state_duration > 0 and self.state_timer >= self.state_duration:
            self._transition_from(self.state)

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

    def _transition_from(self, state: str):
        if state == 'jump':
            if self.is_working:
                self._start_walk()
            else:
                self._set_state('sleep')
        elif state == 'hang':
            if self.is_working:
                self._start_walk()
            else:
                self._set_state('sleep')
        elif state == 'idle':
            if self.is_working:
                self._start_walk()
            else:
                self._set_state('sleep')

    def _start_walk(self):
        if self.x > self.screen_width / 2:
            self.vx = -self.WALK_SPEED
            self.facing_right = False
        else:
            self.vx = self.WALK_SPEED
            self.facing_right = True
        self._set_state('walk')

    def _set_state(self, state: str, duration: float = 0):
        self.state = state
        self.state_timer = 0
        self.state_duration = duration
        if state != 'walk':
            self.vx = 0
            self.vy = 0

    def on_click(self):
        self._set_state('jump', self.JUMP_DURATION)
        if not self.is_working:
            self._show_speech(random.choice(['！？', '干嘛~', '让我睡...']))
        else:
            self._show_speech(random.choice(['呜？', '干嘛~', '嗯？']))

    def on_double_click(self):
        self._set_state('jump', self.JUMP_DURATION)
        self._show_speech(random.choice(['主人！❤️', '嘿！']))

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
            if self.is_working:
                self._start_walk()
            else:
                self._set_state('sleep')

    def on_mouse_near(self, dist: float, mouse_x: float):
        if self.state == 'drag' or self.state == 'sleep' or not self.is_working:
            return
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
            if self.is_working:
                self._start_walk()
            else:
                self._set_state('sleep')
            return
        if dist > 5:
            self.vx = (dx / dist) * self.SPEED_CHASE
            self.vy = (dy / dist) * self.SPEED_CHASE
            self.facing_right = dx > 0
        else:
            self.vx = 0
            self.vy = 0
            if self.is_working:
                self._start_walk()
            else:
                self._set_state('sleep')

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
