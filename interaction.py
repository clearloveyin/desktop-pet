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
