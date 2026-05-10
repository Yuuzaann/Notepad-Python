from __future__ import annotations
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QSpinBox, QGroupBox, QTabWidget,
    QWidget, QFormLayout, QSlider, QFrame, QDialogButtonBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from config.settings import Settings
from themes.theme_manager import AVAILABLE_THEMES, ThemeManager


class SettingsDialog(QDialog):
    theme_changed = Signal(str)
    settings_applied = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._settings = Settings()
        self._theme_manager = ThemeManager()
        self.setWindowTitle("Settings")
        self.setMinimumSize(520, 480)
        self.setModal(True)
        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title_font = QFont("Segoe UI", 16)
        title_font.setWeight(QFont.Weight.Light)
        title.setFont(title_font)
        title.setObjectName("title")

        tabs = QTabWidget()

        appearance_tab = self._build_appearance_tab()
        editor_tab = self._build_editor_tab()
        files_tab = self._build_files_tab()

        tabs.addTab(appearance_tab, "Appearance")
        tabs.addTab(editor_tab, "Editor")
        tabs.addTab(files_tab, "Files")

        btn_box = QHBoxLayout()
        self._apply_btn = QPushButton("Apply")
        self._ok_btn = QPushButton("OK")
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setObjectName("secondary")
        self._reset_btn = QPushButton("Reset")
        self._reset_btn.setObjectName("secondary")

        self._apply_btn.clicked.connect(self._apply)
        self._ok_btn.clicked.connect(self._ok)
        self._cancel_btn.clicked.connect(self.reject)
        self._reset_btn.clicked.connect(self._reset)

        btn_box.addWidget(self._reset_btn)
        btn_box.addStretch()
        btn_box.addWidget(self._cancel_btn)
        btn_box.addWidget(self._apply_btn)
        btn_box.addWidget(self._ok_btn)

        layout.addWidget(title)
        layout.addWidget(tabs)
        layout.addLayout(btn_box)

    def _build_appearance_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(AVAILABLE_THEMES)
        self._theme_combo.currentTextChanged.connect(self._preview_theme)
        layout.addRow("Theme:", self._theme_combo)

        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(8, 32)
        layout.addRow("Font size:", self._font_size_spin)

        self._show_minimap_cb = QCheckBox("Show minimap")
        layout.addRow("Minimap:", self._show_minimap_cb)

        self._show_toolbar_cb = QCheckBox("Show toolbar")
        layout.addRow("Toolbar:", self._show_toolbar_cb)

        return widget

    def _build_editor_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        self._tab_size_spin = QSpinBox()
        self._tab_size_spin.setRange(1, 16)
        layout.addRow("Tab size:", self._tab_size_spin)

        self._use_spaces_cb = QCheckBox("Insert spaces instead of tabs")
        layout.addRow("Spaces:", self._use_spaces_cb)

        self._auto_indent_cb = QCheckBox("Enable auto indentation")
        layout.addRow("Auto indent:", self._auto_indent_cb)

        self._match_brackets_cb = QCheckBox("Highlight matching brackets")
        layout.addRow("Brackets:", self._match_brackets_cb)

        self._line_numbers_cb = QCheckBox("Show line numbers")
        layout.addRow("Line numbers:", self._line_numbers_cb)

        self._highlight_line_cb = QCheckBox("Highlight current line")
        layout.addRow("Current line:", self._highlight_line_cb)

        self._word_wrap_cb = QCheckBox("Word wrap")
        layout.addRow("Word wrap:", self._word_wrap_cb)

        return widget

    def _build_files_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        self._auto_save_cb = QCheckBox("Enable auto save")
        layout.addRow("Auto save:", self._auto_save_cb)

        self._auto_save_interval_spin = QSpinBox()
        self._auto_save_interval_spin.setRange(5, 300)
        self._auto_save_interval_spin.setSuffix(" sec")
        layout.addRow("Interval:", self._auto_save_interval_spin)

        self._restore_tabs_cb = QCheckBox("Restore tabs on startup")
        layout.addRow("Restore tabs:", self._restore_tabs_cb)

        self._backup_cb = QCheckBox("Enable file backup")
        layout.addRow("Backup:", self._backup_cb)

        self._encoding_combo = QComboBox()
        self._encoding_combo.addItems(["UTF-8", "UTF-16", "Latin-1", "CP1252", "ASCII"])
        layout.addRow("Default encoding:", self._encoding_combo)

        return widget

    def _load_values(self) -> None:
        s = self._settings

        theme = s.get("theme", "Dark")
        idx = self._theme_combo.findText(theme)
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)
        self._font_size_spin.setValue(s.get("font_size", 13))
        self._show_minimap_cb.setChecked(s.get("show_minimap", True))
        self._show_toolbar_cb.setChecked(s.get("show_toolbar", True))

        self._tab_size_spin.setValue(s.get("tab_size", 4))
        self._use_spaces_cb.setChecked(s.get("use_spaces", True))
        self._auto_indent_cb.setChecked(s.get("auto_indent", True))
        self._match_brackets_cb.setChecked(s.get("match_brackets", True))
        self._line_numbers_cb.setChecked(s.get("show_line_numbers", True))
        self._highlight_line_cb.setChecked(s.get("highlight_current_line", True))
        self._word_wrap_cb.setChecked(s.get("word_wrap", False))

        self._auto_save_cb.setChecked(s.get("auto_save", True))
        self._auto_save_interval_spin.setValue(s.get("auto_save_interval", 30000) // 1000)
        self._restore_tabs_cb.setChecked(s.get("restore_tabs", True))
        self._backup_cb.setChecked(s.get("backup_enabled", True))
        enc_idx = self._encoding_combo.findText(s.get("encoding", "UTF-8"))
        if enc_idx >= 0:
            self._encoding_combo.setCurrentIndex(enc_idx)

    def _preview_theme(self, theme: str) -> None:
        self._theme_manager.apply_theme(theme)
        self.theme_changed.emit(theme)

    def _apply(self) -> None:
        s = self._settings

        s.set("theme", self._theme_combo.currentText())
        s.set("font_size", self._font_size_spin.value())
        s.set("show_minimap", self._show_minimap_cb.isChecked())
        s.set("show_toolbar", self._show_toolbar_cb.isChecked())

        s.set("tab_size", self._tab_size_spin.value())
        s.set("use_spaces", self._use_spaces_cb.isChecked())
        s.set("auto_indent", self._auto_indent_cb.isChecked())
        s.set("match_brackets", self._match_brackets_cb.isChecked())
        s.set("show_line_numbers", self._line_numbers_cb.isChecked())
        s.set("highlight_current_line", self._highlight_line_cb.isChecked())
        s.set("word_wrap", self._word_wrap_cb.isChecked())

        s.set("auto_save", self._auto_save_cb.isChecked())
        s.set("auto_save_interval", self._auto_save_interval_spin.value() * 1000)
        s.set("restore_tabs", self._restore_tabs_cb.isChecked())
        s.set("backup_enabled", self._backup_cb.isChecked())
        s.set("encoding", self._encoding_combo.currentText())
        s.save()
        self.settings_applied.emit()

    def _ok(self) -> None:
        self._apply()
        self.accept()

    def _reset(self) -> None:
        self._settings.reset()
        self._load_values()
        self._theme_manager.apply_theme(self._settings.get("theme", "Dark"))
        self.theme_changed.emit(self._settings.get("theme", "Dark"))
