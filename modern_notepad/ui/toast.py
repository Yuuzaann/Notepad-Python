from __future__ import annotations
from typing import Optional
from PySide6.QtWidgets import QLabel, QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont


class Toast(QLabel):
    def __init__(self, message: str, parent: Optional[QWidget] = None, duration: int = 2500) -> None:
        super().__init__(message, parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        font = QFont("Segoe UI", 11)
        self.setFont(font)
        self.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
                padding: 10px 20px;
            }
        """)
        self.adjustSize()
        self.setMinimumWidth(200)
        self.setMaximumWidth(500)
        self._bg_color = QColor(40, 40, 40, 230)
        self._duration = duration
        self._opacity = 0.0

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        rect = self.rect().adjusted(2, 2, -2, -2)
        path.addRoundedRect(rect, 10, 10)
        painter.fillPath(path, self._bg_color)
        super().paintEvent(event)

    def show_toast(self) -> None:
        if self.parent():
            parent_rect = self.parent().rect()
            x = parent_rect.width() // 2 - self.width() // 2
            y = parent_rect.height() - 80
            self.move(x, y)
        self.show()
        self.raise_()

        self._fade_in = QPropertyAnimation(self, b"windowOpacity")
        self._fade_in.setDuration(200)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_in.start()

        QTimer.singleShot(self._duration, self._fade_out)

    def _fade_out(self) -> None:
        self._fade_out_anim = QPropertyAnimation(self, b"windowOpacity")
        self._fade_out_anim.setDuration(300)
        self._fade_out_anim.setStartValue(1.0)
        self._fade_out_anim.setEndValue(0.0)
        self._fade_out_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out_anim.finished.connect(self.deleteLater)
        self._fade_out_anim.start()


def show_toast(message: str, parent: Optional[QWidget] = None, duration: int = 2500) -> None:
    toast = Toast(message, parent, duration)
    toast.adjustSize()
    toast.show_toast()
