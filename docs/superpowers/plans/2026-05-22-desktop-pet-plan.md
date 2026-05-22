# Luo Xiaohei Desktop Pet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a macOS desktop pet app that renders Luo Xiaohei procedurally using PyQt6 + QML, with free-roaming behavior and mouse interaction, packaged as a standalone .app.

**Architecture:** Python 3.10+ app with PyQt6 embedding a QML scene via QQuickWidget. A plain Python `Pet` class manages the state machine. A `Renderer` bridges pet state to QML context properties. An `Interaction` module handles mouse events on the widget. A `Canvas` in QML procedurally draws Luo Xiaohei each frame.

**Tech Stack:** Python 3.10, PyQt6, QML (Qt Quick), Canvas API, PyInstaller

---

### Task 1: Project scaffold and dependencies

**Files:**
- Create: `requirements.txt`
- Create: `desktop-pet/build.spec`

- [ ] **Step 1: Write requirements.txt**

```
PyQt6==6.7.0
pyinstaller==6.10.0
```

- [ ] **Step 2: Install dependencies**

Run:
```bash
pip3 install -r requirements.txt
```

Expected: PyQt6 and pyinstaller installed successfully.

- [ ] **Step 3: Verify PyQt6 works**

Run:
```bash
python3 -c "from PyQt6.QtCore import QVersionNumber; print('PyQt6 OK')"
```

Expected: `PyQt6 OK`

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: add PyQt6 and PyInstaller dependencies"
```

### Task 2: Pet state machine

**Files:**
- Create: `pet.py`
- Test: manual verification via Python script

- [ ] **Step 1: Write pet.py**

This is a pure Python class with no Qt dependency. It manages state transitions, timing, position, and interaction responses.

```python
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
```

- [ ] **Step 2: Write and run pet unit test**

```python
# test_pet.py
from pet import Pet
import time

def test_initial_state():
    p = Pet(800, 600)
    assert p.state == 'idle'
    assert p.x == 400
    assert p.y == 300

def test_click_triggers_jump():
    p = Pet(800, 600)
    p.on_click()
    assert p.state == 'jump'
    assert p.state_duration == 600

def test_double_click():
    p = Pet(800, 600)
    p.on_double_click()
    assert p.state == 'jump'

def test_drag_sequence():
    p = Pet(800, 600)
    p.on_drag_start()
    assert p.state == 'drag'
    p.on_drag_move(100, 100)
    assert p.x == 100
    assert p.y == 100
    p.on_drag_end(100, 100)
    assert p.state == 'idle'

def test_drag_to_edge_hangs():
    p = Pet(800, 600)
    p.on_drag_end(5, 5)
    assert p.state == 'hang'

def test_sleep_after_timeout():
    p = Pet(800, 600)
    p.last_interaction_time = time.time() * 1000 - 20000
    p.update(100)
    assert p.state == 'sleep'

def test_click_wakes_from_sleep():
    p = Pet(800, 600)
    p.state = 'sleep'
    p.on_click()
    assert p.state == 'jump'

def test_chase_mouse():
    p = Pet(800, 600)
    p.on_mouse_near(50, 500)
    assert p.state == 'chase'
    p.update_chase_target(500, 300)
    assert p.vx > 0

def test_speech_bubble():
    p = Pet(800, 600)
    p.on_click()
    assert p.get_speech() != ''

def test_walk_transition():
    p = Pet(800, 600)
    p._start_walk()
    assert p.state == 'walk'

def test_update_with_timer():
    p = Pet(800, 600)
    p.state = 'walk'
    p.state_duration = 100
    p.state_timer = 0
    p.update(200)
    assert p.state == 'idle'

if __name__ == '__main__':
    test_initial_state()
    test_click_triggers_jump()
    test_double_click()
    test_drag_sequence()
    test_drag_to_edge_hangs()
    test_sleep_after_timeout()
    test_click_wakes_from_sleep()
    test_chase_mouse()
    test_speech_bubble()
    test_walk_transition()
    test_update_with_timer()
    print('All tests passed!')
```

Run:
```bash
python3 test_pet.py
```

Expected: `All tests passed!`

- [ ] **Step 3: Commit**

```bash
git add pet.py test_pet.py
git commit -m "feat: add pet state machine with full test coverage"
```

### Task 3: QML Canvas drawing of Luo Xiaohei

**Files:**
- Create: `resources/ui/PetPanel.qml`

This QML file contains the entire visual rendering: Canvas drawing of Luo Xiaohei, frame animation via QML Timer, and speech bubble overlay.

- [ ] **Step 1: Write PetPanel.qml**

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    width: 200
    height: 200

    property real petX: 100
    property real petY: 100
    property string petState: "idle"
    property bool facingRight: true
    property string bubbleText: ""
    property bool bubbleVisible: false

    property real animFrame: 0
    property real bodyBob: 0
    property real tailAngle: 0
    property real eyeScale: 1.0
    property real legAngle: 0
    property real sleepZ: 0

    Timer {
        interval: 33
        running: true
        repeat: true
        onTriggered: {
            animFrame = (animFrame + 1) % 360
            var t = animFrame * 0.01745

            if (petState === "idle") {
                bodyBob = Math.sin(t * 0.5) * 3
                tailAngle = Math.sin(t * 0.67) * 0.26
                legAngle = 0
            } else if (petState === "walk") {
                bodyBob = Math.sin(t * 4) * 2
                tailAngle = Math.sin(t * 5) * 0.4
                legAngle = Math.sin(t * 4)
            } else if (petState === "jump") {
                var jumpProgress = (animFrame % 18) / 18
                bodyBob = -Math.sin(jumpProgress * Math.PI) * 40
                eyeScale = 1 + Math.sin(jumpProgress * Math.PI * 2) * 0.3
                tailAngle = Math.sin(t * 2) * 0.3
                legAngle = Math.sin(t * 3)
            } else if (petState === "sleep") {
                bodyBob = 5
                tailAngle = 0
                legAngle = 0
                sleepZ = (sleepZ + 0.02) % 1
            } else if (petState === "chase") {
                bodyBob = Math.sin(t * 5) * 2
                tailAngle = Math.sin(t * 6) * 0.5
                legAngle = Math.sin(t * 6)
            } else if (petState === "drag") {
                bodyBob = -10
                tailAngle = Math.sin(t * 3) * 0.5
                legAngle = Math.sin(t * 5)
            } else if (petState === "hang") {
                bodyBob = -5
                tailAngle = 0
                legAngle = 0
            }

            canvas.requestPaint()
        }
    }

    Canvas {
        id: canvas
        anchors.fill: parent

        onPaint: {
            var ctx = canvas.getContext("2d")
            ctx.clearRect(0, 0, canvas.width, canvas.height)

            var cx = petX
            var cy = petY + bodyBob
            var scale = 1.0

            ctx.save()
            if (!facingRight) {
                ctx.translate(canvas.width, 0)
                ctx.scale(-1, 1)
                cx = canvas.width - petX
            }

            // --- tail ---
            ctx.save()
            ctx.translate(cx - 12, cy + 15)
            ctx.rotate(tailAngle * 0.5)
            ctx.fillStyle = "#1a1a1a"
            ctx.beginPath()
            ctx.ellipse(-8, -3, 16, 6)
            ctx.fill()
            ctx.restore()

            // tail stroke
            ctx.strokeStyle = "#1a1a1a"
            ctx.lineWidth = 6
            ctx.lineCap = "round"
            ctx.beginPath()
            ctx.moveTo(cx - 12, cy + 15)
            var tailTipX = cx - 12 + Math.sin(tailAngle) * 30
            var tailTipY = cy + 15 + Math.cos(tailAngle) * 10 - 15
            ctx.quadraticCurveTo(cx - 20, cy + 5, tailTipX, tailTipY)
            ctx.stroke()

            // --- body ---
            ctx.fillStyle = "#1a1a1a"
            ctx.beginPath()
            ctx.ellipse(cx, cy + 5, 22, 20)
            ctx.fill()

            // legs
            var legSwing = legAngle * 0.3
            ctx.fillStyle = "#1a1a1a"
            // front legs
            ctx.beginPath()
            ctx.ellipse(cx - 10 + legSwing * 5, cy + 22, 6, 8)
            ctx.fill()
            ctx.beginPath()
            ctx.ellipse(cx + 10 - legSwing * 5, cy + 22, 6, 8)
            ctx.fill()
            // back legs (smaller)
            ctx.beginPath()
            ctx.ellipse(cx - 14 + legSwing * 3, cy + 20, 4, 6)
            ctx.fill()
            ctx.beginPath()
            ctx.ellipse(cx + 14 - legSwing * 3, cy + 20, 4, 6)
            ctx.fill()

            // --- head ---
            ctx.fillStyle = "#1a1a1a"
            ctx.beginPath()
            ctx.arc(cx, cy - 10, 18, 0, Math.PI * 2)
            ctx.fill()

            // ears
            ctx.beginPath()
            ctx.moveTo(cx - 14, cy - 18)
            ctx.lineTo(cx - 20, cy - 35)
            ctx.lineTo(cx - 6, cy - 22)
            ctx.closePath()
            ctx.fill()
            ctx.beginPath()
            ctx.moveTo(cx + 14, cy - 18)
            ctx.lineTo(cx + 20, cy - 35)
            ctx.lineTo(cx + 6, cy - 22)
            ctx.closePath()
            ctx.fill()

            // inner ears
            ctx.fillStyle = "#2a2a2a"
            ctx.beginPath()
            ctx.moveTo(cx - 13, cy - 20)
            ctx.lineTo(cx - 17, cy - 31)
            ctx.lineTo(cx - 8, cy - 23)
            ctx.closePath()
            ctx.fill()
            ctx.beginPath()
            ctx.moveTo(cx + 13, cy - 20)
            ctx.lineTo(cx + 17, cy - 31)
            ctx.lineTo(cx + 8, cy - 23)
            ctx.closePath()
            ctx.fill()

            // --- eyes ---
            if (petState === "sleep") {
                ctx.strokeStyle = "#111111"
                ctx.lineWidth = 2
                ctx.beginPath()
                ctx.arc(cx - 8, cy - 8, 6, 0, Math.PI)
                ctx.stroke()
                ctx.beginPath()
                ctx.arc(cx + 8, cy - 8, 6, 0, Math.PI)
                ctx.stroke()
            } else {
                var eyeW = 7 * eyeScale
                var eyeH = 7 * eyeScale
                // left eye
                ctx.fillStyle = "#ffdd44"
                ctx.beginPath()
                ctx.ellipse(cx - 8, cy - 10, eyeW, eyeH)
                ctx.fill()
                // right eye
                ctx.beginPath()
                ctx.ellipse(cx + 8, cy - 10, eyeW, eyeH)
                ctx.fill()
                // pupils
                ctx.fillStyle = "#111111"
                ctx.beginPath()
                ctx.ellipse(cx - 7, cy - 9, 3, 4)
                ctx.fill()
                ctx.beginPath()
                ctx.ellipse(cx + 9, cy - 9, 3, 4)
                ctx.fill()
                // highlights
                ctx.fillStyle = "#ffffff"
                ctx.beginPath()
                ctx.arc(cx - 6, cy - 12, 1.5, 0, Math.PI * 2)
                ctx.fill()
                ctx.beginPath()
                ctx.arc(cx + 10, cy - 12, 1.5, 0, Math.PI * 2)
                ctx.fill()
            }

            // --- mouth ---
            if (petState === "jump" || petState === "drag") {
                ctx.fillStyle = "#e88"
                ctx.beginPath()
                ctx.arc(cx, cy - 2, 4, 0, Math.PI)
                ctx.fill()
            } else if (petState !== "sleep") {
                ctx.strokeStyle = "#111111"
                ctx.lineWidth = 1.5
                ctx.beginPath()
                ctx.arc(cx, cy - 4, 4, 0.2, Math.PI - 0.2)
                ctx.stroke()
            }

            // Zzz for sleep
            if (petState === "sleep") {
                ctx.fillStyle = "#888888"
                ctx.font = "12px sans-serif"
                var z = sleepZ
                if (z > 0) ctx.fillText("z", cx + 20, cy - 30)
                if (z > 0.3) ctx.fillText("z", cx + 28, cy - 40)
                if (z > 0.6) ctx.fillText("Z", cx + 36, cy - 50)
            }

            ctx.restore()
        }
    }

    // Speech bubble
    Rectangle {
        id: bubble
        visible: bubbleVisible && bubbleText.length > 0
        x: facingRight ? petX + 20 : petX - 20 - bubbleContent.width - 20
        y: petY - 50
        width: bubbleContent.width + 20
        height: bubbleContent.height + 12
        radius: 10
        color: "#ffffff"
        opacity: 0.92

        Text {
            id: bubbleContent
            anchors.centerIn: parent
            text: bubbleText
            font.pixelSize: 12
            color: "#333333"
        }

        Rectangle {
            x: facingRight ? 10 : parent.width - 30
            y: parent.height - 4
            width: 8
            height: 8
            rotation: 45
            color: parent.color
        }
    }
}
```

- [ ] **Step 2: Write a standalone QML test**

Create a minimal `test_qml.html` or test with `qmlscene` approach. Since QML Canvas can't be easily automated, verify by running:

```bash
python3 -c "
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
import sys
app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()
engine.load('resources/ui/PetPanel.qml')
print('QML loaded without errors')
"
```

Expected: `QML loaded without errors`

- [ ] **Step 3: Commit**

```bash
git add resources/ui/PetPanel.qml
git commit -m "feat: add QML Canvas rendering for Luo Xiaohei"
```

### Task 4: Renderer bridge

**Files:**
- Create: `renderer.py`

This bridges the Pet state to QML properties. It attaches to the QQuickWidget's root context and syncs pet state each frame.

- [ ] **Step 1: Write renderer.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add renderer.py
git commit -m "feat: add PetBridge to sync state into QML context"
```

### Task 5: Interaction module

**Files:**
- Create: `interaction.py`

Handles mouse event processing: click detection, double-click timing, drag logic, and proximity detection.

- [ ] **Step 1: Write interaction.py**

```python
from PyQt6.QtCore import QObject, QEvent, QPointF, Qt
from PyQt6.QtQuickWidgets import QQuickWidget
from pet import Pet
import math


class Interaction:
    def __init__(self, widget: QQuickWidget, pet: Pet):
        self.widget = widget
        self.pet = pet
        self._dragging = False
        self._drag_offset_x = 0.0
        self._drag_offset_y = 0.0
        self._last_click_time = 0
        self._last_click_x = 0.0
        self._last_click_y = 0.0
        self._double_click_distance = 10

        widget.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            self._on_mouse_press(event)
            return True
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self._on_mouse_release(event)
            return True
        elif event.type() == QEvent.Type.MouseMove:
            self._on_mouse_move(event)
            return True
        return False

    def _get_pet_screen_pos(self):
        return QPointF(self.pet.x, self.pet.y)

    def _dist_to_pet(self, pos: QPointF) -> float:
        pet_pos = self._get_pet_screen_pos()
        dx = pos.x() - pet_pos.x()
        dy = pos.y() - pet_pos.y()
        return math.hypot(dx, dy)

    def _on_mouse_press(self, event):
        pos = event.position()
        dist = self._dist_to_pet(pos)
        if event.button() == Qt.MouseButton.LeftButton and dist < 50:
            self._dragging = True
            pet_pos = self._get_pet_screen_pos()
            self._drag_offset_x = pet_pos.x() - pos.x()
            self._drag_offset_y = pet_pos.y() - pos.y()
            self.pet.on_drag_start()

    def _on_mouse_release(self, event):
        pos = event.position()
        if self._dragging:
            self._dragging = False
            self.pet.on_drag_end(
                pos.x() + self._drag_offset_x,
                pos.y() + self._drag_offset_y
            )
            return

        if event.button() == Qt.MouseButton.LeftButton:
            dist = self._dist_to_pet(pos)
            if dist < 50:
                now = event.timestamp()
                dt = now - self._last_click_time
                dx = abs(pos.x() - self._last_click_x)
                dy = abs(pos.y() - self._last_click_y)
                if (dt < 400 and dx < self._double_click_distance
                        and dy < self._double_click_distance):
                    self.pet.on_double_click()
                else:
                    self.pet.on_click()
                self._last_click_time = now
                self._last_click_x = pos.x()
                self._last_click_y = pos.y()

    def _on_mouse_move(self, event):
        pos = event.position()
        if self._dragging:
            self.pet.on_drag_move(
                pos.x() + self._drag_offset_x,
                pos.y() + self._drag_offset_y
            )
            return
        dist = self._dist_to_pet(pos)
        self.pet.on_mouse_near(dist, pos.x())
        self.pet.update_chase_target(pos.x(), pos.y())
```

- [ ] **Step 2: Commit**

```bash
git add interaction.py
git commit -m "feat: add mouse interaction handling"
```

### Task 6: Main application entry point

**Files:**
- Create: `main.py`

This ties everything together: creates the QApplication, sets up the QQuickWidget with PetPanel.qml, configures transparent window behavior, runs the game loop.

- [ ] **Step 1: Write main.py**

```python
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
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 200)
        self.move_to_bottom_right()

        # Pet
        self.pet = Pet(self.width(), self.height())

        # QML
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.qml_widget = QQuickWidget()
        self.qml_widget.setClearColor(Qt.GlobalColor.transparent)
        self.qml_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.qml_widget.setSource(QUrl.fromLocalFile('resources/ui/PetPanel.qml'))
        self.qml_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        layout.addWidget(self.qml_widget)

        # Bridge
        self.bridge = PetBridge(self.pet)
        root_context = self.qml_widget.rootContext()
        root_context.setContextProperty('petBridge', self.bridge)

        # Connect bridge signals to update QML properties
        self.bridge.stateChanged.connect(self._update_qml_state)
        self.bridge.positionChanged.connect(self._update_qml_position)
        self.bridge.facingChanged.connect(self._update_qml_facing)
        self.bridge.bubbleChanged.connect(self._update_qml_bubble)

        # Interaction
        self.interaction = Interaction(self.qml_widget, self.pet)

        # Game loop
        self.last_time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._game_loop)
        self.timer.start(33)

        # Tray icon
        self._setup_tray()

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

    def move_to_bottom_right(self):
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.right() - self.width() - 20
            y = geometry.bottom() - self.height() - 20
            self.move(int(x), int(y))

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
```

- [ ] **Step 2: Run the application**

```bash
python3 main.py
```

Expected: A window appears in the bottom right corner showing Luo Xiaohei.

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add main application entry with window and game loop"
```

### Task 7: Integration test and polish

- [ ] **Step 1: Test all interactions**

1. Click the pet → should jump + show speech bubble
2. Double click → higher jump + happy speech
3. Drag the pet → should follow mouse, show drag speech
4. Drag to screen edge → should hang
5. Stop interacting for 15s → should fall asleep
6. Click while sleeping → should wake up startled
7. Move mouse near → should chase

- [ ] **Step 2: Check window transparency**

Verify the background is fully transparent and the pet renders cleanly without artifacts.

- [ ] **Step 3: Commit any fixes**

```bash
git add -A && git commit -m "fix: polish interactions and rendering"
```

### Task 8: PyInstaller packaging

**Files:**
- Modify: `build.spec`

- [ ] **Step 1: Write build.spec**

```python
# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/ui/PetPanel.qml', 'resources/ui'),
    ],
    hiddenimports=[
        'PyQt6.QtQml',
        'PyQt6.QtQuick',
        'PyQt6.QtNetwork',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='罗小黑桌宠',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    a.binaries,
    a.datas,
    [],
    name='罗小黑桌宠.app',
    icon=None,
    display_name='罗小黑桌宠',
    version='1.0.0',
    bundle_identifier='com.luoxiaohei.desktop-pet',
)
```

- [ ] **Step 2: Build**

```bash
pyinstaller build.spec
```

Expected: `dist/罗小黑桌宠.app` is created.

- [ ] **Step 3: Test the .app**

```bash
open "dist/罗小黑桌宠.app"
```

Expected: The app runs as a standalone macOS application.

- [ ] **Step 4: Commit**

```bash
git add build.spec
git commit -m "chore: add PyInstaller build config"
```
