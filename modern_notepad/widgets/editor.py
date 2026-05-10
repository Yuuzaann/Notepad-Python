from __future__ import annotations
import re
from typing import Optional, List
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PySide6.QtCore import (
    Qt, QRect, QSize, Signal, QTimer, QRegularExpression
)
from PySide6.QtGui import (
    QColor, QPainter, QFont, QTextFormat, QTextCursor,
    QTextCharFormat, QKeyEvent, QFontMetrics, QPaintEvent,
    QResizeEvent
)
from .line_number_area import LineNumberArea


class CodeEditor(QPlainTextEdit):
    cursor_position_changed_signal = Signal(int, int)
    content_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._line_number_area = LineNumberArea(self)
        self._tab_size = 4
        self._use_spaces = True
        self._auto_indent = True
        self._match_brackets = True
        self._zoom_level = 100
        self._base_font_size = 13
        self._highlight_color = QColor("#2a2d2e")
        self._line_number_bg = QColor("#1e1e1e")
        self._line_number_fg = QColor("#858585")
        self._search_highlights: List[QTextEdit.ExtraSelection] = []

        self._setup_font()
        self._connect_signals()
        self._update_line_number_area_width(0)
        self._highlight_current_line()

    def _setup_font(self) -> None:
        font = QFont()
        font.setFamily("Consolas")
        font.setFixedPitch(True)
        font.setPointSize(self._base_font_size)
        self.setFont(font)
        tab_stop = QFontMetrics(font).horizontalAdvance(" ") * self._tab_size
        self.setTabStopDistance(tab_stop)

    def _connect_signals(self) -> None:
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._on_cursor_changed)
        self.textChanged.connect(self.content_changed.emit)

    def _on_cursor_changed(self) -> None:
        self._highlight_current_line()
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1
        self.cursor_position_changed_signal.emit(line, col)

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        font_metrics = QFontMetrics(self.font())
        return 16 + font_metrics.horizontalAdvance("9") * digits

    def _update_line_number_area_width(self, _: int = 0) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(
                0, rect.y(), self._line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event: QPaintEvent) -> None:
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), self._line_number_bg)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        font = self.font()
        font_metrics = QFontMetrics(font)
        line_height = font_metrics.height()

        current_block = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if block_number == current_block:
                    painter.setPen(QColor("#cccccc"))
                else:
                    painter.setPen(self._line_number_fg)
                painter.drawText(
                    0, top,
                    self._line_number_area.width() - 4,
                    line_height,
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def _highlight_current_line(self) -> None:
        selections: List[QTextEdit.ExtraSelection] = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(self._highlight_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)

        all_selections = selections + self._search_highlights
        self.setExtraSelections(all_selections)

    def set_search_highlights(self, positions: List[tuple]) -> None:
        self._search_highlights = []
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#515c00"))
        fmt.setForeground(QColor("#ffffff"))
        for start, length in positions:
            selection = QTextEdit.ExtraSelection()
            selection.format = fmt
            cursor = self.textCursor()
            cursor.setPosition(start)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                length,
            )
            selection.cursor = cursor
            self._search_highlights.append(selection)
        self._highlight_current_line()

    def clear_search_highlights(self) -> None:
        self._search_highlights = []
        self._highlight_current_line()

    def set_theme_colors(self, theme: str) -> None:
        palette = {
            "dark": ("#2a2d2e", "#1e1e1e", "#858585"),
            "light": ("#e8f0fe", "#f3f3f3", "#a0a0a0"),
            "dracula": ("#44475a", "#282a36", "#6272a4"),
            "midnight": ("#1a2540", "#0a0e1a", "#1e3a5f"),
        }
        colors = palette.get(theme.lower(), palette["dark"])
        self._highlight_color = QColor(colors[0])
        self._line_number_bg = QColor(colors[1])
        self._line_number_fg = QColor(colors[2])
        self._highlight_current_line()
        self._line_number_area.update()

    def zoom_in(self, step: int = 2) -> None:
        self._zoom_level = min(self._zoom_level + step * 10, 300)
        self._apply_zoom()

    def zoom_out(self, step: int = 2) -> None:
        self._zoom_level = max(self._zoom_level - step * 10, 50)
        self._apply_zoom()

    def reset_zoom(self) -> None:
        self._zoom_level = 100
        self._apply_zoom()

    def _apply_zoom(self) -> None:
        size = int(self._base_font_size * self._zoom_level / 100)
        font = self.font()
        font.setPointSize(max(6, size))
        self.setFont(font)
        tab_stop = QFontMetrics(font).horizontalAdvance(" ") * self._tab_size
        self.setTabStopDistance(tab_stop)

    @property
    def zoom_level(self) -> int:
        return self._zoom_level

    def set_font_size(self, size: int) -> None:
        self._base_font_size = size
        self._apply_zoom()

    def set_tab_size(self, size: int) -> None:
        self._tab_size = size
        font = self.font()
        tab_stop = QFontMetrics(font).horizontalAdvance(" ") * size
        self.setTabStopDistance(tab_stop)

    def set_use_spaces(self, use_spaces: bool) -> None:
        self._use_spaces = use_spaces

    def get_stats(self) -> dict:
        text = self.toPlainText()
        cursor = self.textCursor()
        return {
            "line": cursor.blockNumber() + 1,
            "col": cursor.positionInBlock() + 1,
            "lines": self.blockCount(),
            "words": len(text.split()) if text.strip() else 0,
            "chars": len(text),
        }

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_Tab:
            if self._use_spaces:
                cursor = self.textCursor()
                if cursor.hasSelection():
                    self._indent_selection()
                    return
                self.insertPlainText(" " * self._tab_size)
                return

        if key == Qt.Key.Key_Backtab:
            self._unindent_selection()
            return

        if key == Qt.Key.Key_Return and self._auto_indent:
            cursor = self.textCursor()
            block_text = cursor.block().text()
            indent = ""
            for ch in block_text:
                if ch in (" ", "\t"):
                    indent += ch
                else:
                    break
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return

        if key in (Qt.Key.Key_BraceLeft, Qt.Key.Key_BracketLeft, Qt.Key.Key_ParenLeft) and self._match_brackets:
            pairs = {
                Qt.Key.Key_BraceLeft: ("{"  , "}"),
                Qt.Key.Key_BracketLeft: ("[", "]"),
                Qt.Key.Key_ParenLeft: ("(", ")"),
            }
            open_ch, close_ch = pairs[key]
            cursor = self.textCursor()
            if cursor.hasSelection():
                selected = cursor.selectedText()
                cursor.insertText(f"{open_ch}{selected}{close_ch}")
                return

        if key == Qt.Key.Key_Equal and modifiers == Qt.KeyboardModifier.ControlModifier:
            self.zoom_in()
            return
        if key == Qt.Key.Key_Minus and modifiers == Qt.KeyboardModifier.ControlModifier:
            self.zoom_out()
            return
        if key == Qt.Key.Key_0 and modifiers == Qt.KeyboardModifier.ControlModifier:
            self.reset_zoom()
            return

        super().keyPressEvent(event)

    def _indent_selection(self) -> None:
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.beginEditBlock()
        while cursor.position() <= end:
            cursor.insertText(" " * self._tab_size)
            end += self._tab_size
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        cursor.endEditBlock()

    def _unindent_selection(self) -> None:
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.beginEditBlock()
        while cursor.position() <= end:
            line = cursor.block().text()
            remove = 0
            for ch in line[: self._tab_size]:
                if ch == " ":
                    remove += 1
                elif ch == "\t":
                    remove += 1
                    break
                else:
                    break
            for _ in range(remove):
                cursor.deleteChar()
                end -= 1
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        cursor.endEditBlock()

    def wheelEvent(self, event) -> None:
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in(1)
            else:
                self.zoom_out(1)
            event.accept()
        else:
            super().wheelEvent(event)
