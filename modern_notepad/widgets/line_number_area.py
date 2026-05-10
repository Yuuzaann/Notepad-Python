from __future__ import annotations
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize, Qt, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QTextBlock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .editor import CodeEditor


class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self._editor = editor
        self.setObjectName("lineNumberArea")

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        self._editor.line_number_area_paint_event(event)
