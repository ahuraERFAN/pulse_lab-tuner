from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import QTimer
import math


class TunerMeter(QWidget):
    def __init__(self):
        super().__init__()

        self.current_cents = 0
        self.display_cents = 0

        self.setMinimumHeight(200)

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    # ----------------------

    def set_cents(self, cents):
        self.current_cents = max(-50, min(50, cents))

    # ----------------------

    def animate(self):
        self.display_cents += (self.current_cents - self.display_cents) * 0.2
        self.update()

    # ----------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        center_x = w / 2
        center_y = h * 0.85
        radius = min(w / 2.5, h)

        # Arc
        pen = QPen(QColor("#888"), 3)
        painter.setPen(pen)
        painter.drawArc(
            int(center_x - radius),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2),
            0 * 16,
            180 * 16,
        )

        # Needle
        angle = (self.display_cents / 50) * 90
        rad = math.radians(90 - angle)

        needle_length = radius * 0.9

        x = center_x + needle_length * math.cos(rad)
        y = center_y - needle_length * math.sin(rad)

        if abs(self.display_cents) < 5:
            color = QColor("#00ff88")
        elif abs(self.display_cents) < 15:
            color = QColor("#ffaa00")
        else:
            color = QColor("#ff4444")

        pen = QPen(color, 4)
        painter.setPen(pen)
        painter.drawLine(int(center_x), int(center_y), int(x), int(y))