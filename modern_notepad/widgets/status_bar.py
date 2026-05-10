from __future__ import annotations
from typing import Optional
from PySide6.QtWidgets import QStatusBar, QLabel, QWidget
from PySide6.QtCore import Qt


class StatusBarWidget(QStatusBar):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSizeGripEnabled(False)
        self._build_labels()

    def _make_label(self, text: str = "", min_width: int = 0) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        if min_width:
            label.setMinimumWidth(min_width)
        return label

    def _build_labels(self) -> None:
        sep = "|"

        self._lbl_position = self._make_label("Ln 1, Col 1", 100)
        self._lbl_words = self._make_label("0 words", 80)
        self._lbl_chars = self._make_label("0 chars", 70)
        self._lbl_encoding = self._make_label("UTF-8", 60)
        self._lbl_filetype = self._make_label("Plain Text", 80)
        self._lbl_zoom = self._make_label("100%", 50)
        self._lbl_message = self._make_label("Ready")

        self.addWidget(self._lbl_position)
        self.addWidget(QLabel(sep))
        self.addWidget(self._lbl_words)
        self.addWidget(QLabel(sep))
        self.addWidget(self._lbl_chars)
        self.addWidget(QLabel(sep))
        self.addWidget(self._lbl_encoding)
        self.addWidget(QLabel(sep))
        self.addWidget(self._lbl_filetype)
        self.addWidget(QLabel(sep))
        self.addWidget(self._lbl_zoom)
        self.addPermanentWidget(self._lbl_message)

    def update_position(self, line: int, col: int) -> None:
        self._lbl_position.setText(f"Ln {line}, Col {col}")

    def update_stats(self, words: int, chars: int) -> None:
        self._lbl_words.setText(f"{words:,} words")
        self._lbl_chars.setText(f"{chars:,} chars")

    def update_encoding(self, encoding: str) -> None:
        self._lbl_encoding.setText(encoding)

    def update_filetype(self, filetype: str) -> None:
        self._lbl_filetype.setText(filetype)

    def update_zoom(self, zoom: int) -> None:
        self._lbl_zoom.setText(f"{zoom}%")

    def show_message(self, message: str, timeout: int = 3000) -> None:
        self._lbl_message.setText(message)
        if timeout > 0:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(timeout, lambda: self._lbl_message.setText("Ready"))
