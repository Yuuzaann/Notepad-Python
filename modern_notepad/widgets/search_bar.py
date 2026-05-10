from __future__ import annotations
import re
from typing import Optional, List, Tuple
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton,
    QCheckBox, QLabel, QWidget
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QKeyEvent, QShortcut, QKeySequence


class SearchBar(QFrame):
    search_requested = Signal(str, bool, bool)
    replace_requested = Signal(str, str, bool, bool)
    replace_all_requested = Signal(str, str, bool, bool)
    closed = Signal()
    navigate_next = Signal()
    navigate_prev = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("searchBar")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._build_ui()
        self._connect_signals()
        self.hide()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        find_row = QHBoxLayout()
        find_row.setSpacing(6)

        self._find_input = QLineEdit()
        self._find_input.setPlaceholderText("Find...")
        self._find_input.setMinimumWidth(200)

        self._case_cb = QCheckBox("Aa")
        self._case_cb.setToolTip("Match case")
        self._regex_cb = QCheckBox(".*")
        self._regex_cb.setToolTip("Use regex")

        self._prev_btn = QPushButton("↑")
        self._prev_btn.setFixedSize(28, 28)
        self._prev_btn.setToolTip("Previous match (Shift+Enter)")
        self._next_btn = QPushButton("↓")
        self._next_btn.setFixedSize(28, 28)
        self._next_btn.setToolTip("Next match (Enter)")
        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedSize(28, 28)
        self._close_btn.setObjectName("secondary")
        self._close_btn.setToolTip("Close (Esc)")

        self._match_label = QLabel("")
        self._match_label.setObjectName("subtitle")
        self._match_label.setMinimumWidth(80)

        find_row.addWidget(self._find_input)
        find_row.addWidget(self._case_cb)
        find_row.addWidget(self._regex_cb)
        find_row.addWidget(self._prev_btn)
        find_row.addWidget(self._next_btn)
        find_row.addWidget(self._match_label)
        find_row.addStretch()
        find_row.addWidget(self._close_btn)

        replace_row = QHBoxLayout()
        replace_row.setSpacing(6)

        self._replace_input = QLineEdit()
        self._replace_input.setPlaceholderText("Replace...")
        self._replace_input.setMinimumWidth(200)

        self._replace_btn = QPushButton("Replace")
        self._replace_btn.setFixedHeight(28)
        self._replace_all_btn = QPushButton("Replace All")
        self._replace_all_btn.setFixedHeight(28)

        replace_row.addWidget(self._replace_input)
        replace_row.addWidget(self._replace_btn)
        replace_row.addWidget(self._replace_all_btn)
        replace_row.addStretch()

        layout.addLayout(find_row)
        layout.addLayout(replace_row)

    def _connect_signals(self) -> None:
        self._find_input.textChanged.connect(self._on_find_text_changed)
        self._find_input.returnPressed.connect(self.navigate_next.emit)
        self._case_cb.toggled.connect(self._trigger_search)
        self._regex_cb.toggled.connect(self._trigger_search)
        self._prev_btn.clicked.connect(self.navigate_prev.emit)
        self._next_btn.clicked.connect(self.navigate_next.emit)
        self._close_btn.clicked.connect(self.close_bar)
        self._replace_btn.clicked.connect(self._do_replace)
        self._replace_all_btn.clicked.connect(self._do_replace_all)

        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(200)
        self._debounce_timer.timeout.connect(self._trigger_search)

    def _on_find_text_changed(self) -> None:
        self._debounce_timer.start()

    def _trigger_search(self) -> None:
        text = self._find_input.text()
        self.search_requested.emit(text, self._case_cb.isChecked(), self._regex_cb.isChecked())

    def _do_replace(self) -> None:
        self.replace_requested.emit(
            self._find_input.text(),
            self._replace_input.text(),
            self._case_cb.isChecked(),
            self._regex_cb.isChecked(),
        )

    def _do_replace_all(self) -> None:
        self.replace_all_requested.emit(
            self._find_input.text(),
            self._replace_input.text(),
            self._case_cb.isChecked(),
            self._regex_cb.isChecked(),
        )

    def open_bar(self, selected_text: str = "") -> None:
        self.show()
        if selected_text:
            self._find_input.setText(selected_text)
        self._find_input.selectAll()
        self._find_input.setFocus()

    def close_bar(self) -> None:
        self.hide()
        self.closed.emit()

    def update_match_count(self, current: int, total: int) -> None:
        if total == 0:
            self._match_label.setText("No results")
        else:
            self._match_label.setText(f"{current}/{total}")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close_bar()
        elif event.key() == Qt.Key.Key_Return:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.navigate_prev.emit()
            else:
                self.navigate_next.emit()
        else:
            super().keyPressEvent(event)

    @property
    def find_text(self) -> str:
        return self._find_input.text()

    @property
    def match_case(self) -> bool:
        return self._case_cb.isChecked()

    @property
    def use_regex(self) -> bool:
        return self._regex_cb.isChecked()
