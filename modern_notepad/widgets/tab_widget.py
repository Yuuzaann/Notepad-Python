from __future__ import annotations
import os
from typing import Optional, List, Dict
from PySide6.QtWidgets import (
    QTabWidget, QTabBar, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt, QPoint, QMimeData
from PySide6.QtGui import QDrag, QPixmap, QAction
from .editor import CodeEditor
from utils.syntax_highlighter import SyntaxHighlighter
from models.tab_model import TabModel
from config.settings import Settings


class TabBar(QTabBar):
    tab_close_requested_custom = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.setExpanding(False)
        self.setDrawBase(False)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            index = self.tabAt(event.pos())
            if index >= 0:
                self.tab_close_requested_custom.emit(index)
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            index = self.tabAt(event.pos())
            if index >= 0:
                self.tab_close_requested_custom.emit(index)
                return
        super().mousePressEvent(event)


class EditorTabWidget(QTabWidget):
    tab_modified_changed = Signal(int, bool)
    active_tab_changed = Signal(object)
    no_tabs_remaining = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._settings = Settings()
        self._tab_models: Dict[int, TabModel] = {}
        self._highlighters: Dict[int, SyntaxHighlighter] = {}
        self._current_theme = self._settings.get("theme", "Dark")

        custom_tab_bar = TabBar(self)
        self.setTabBar(custom_tab_bar)
        custom_tab_bar.tab_close_requested_custom.connect(self.close_tab)
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_tab_changed)

        self.setDocumentMode(True)
        self.setMovable(True)

    def add_tab(self, model: TabModel) -> int:
        editor = CodeEditor()
        editor.setPlainText(model.content)
        editor.content_changed.connect(lambda idx=self.count(): self._on_content_changed(idx))

        index = super().addTab(editor, model.display_title)
        self._tab_models[index] = model

        if model.file_path:
            highlighter = SyntaxHighlighter(
                editor.document(), model.file_path, self._current_theme
            )
            self._highlighters[index] = highlighter

        editor.set_theme_colors(self._current_theme.lower())
        editor.set_font_size(self._settings.get("font_size", 13))
        editor.set_tab_size(self._settings.get("tab_size", 4))
        editor.set_use_spaces(self._settings.get("use_spaces", True))

        cursor = editor.textCursor()
        cursor.setPosition(min(model.cursor_position, len(model.content)))
        editor.setTextCursor(cursor)

        editor.content_changed.connect(
            lambda: self._mark_modified(self.indexOf(editor))
        )
        self.setCurrentIndex(index)
        return index

    def _mark_modified(self, index: int) -> None:
        if index < 0 or index not in self._tab_models:
            return
        model = self._tab_models[index]
        if not model.is_modified:
            model.is_modified = True
            self.setTabText(index, model.display_title)
            self.tab_modified_changed.emit(index, True)

    def _on_content_changed(self, index: int) -> None:
        pass

    def _on_tab_changed(self, index: int) -> None:
        model = self._tab_models.get(index)
        self.active_tab_changed.emit(model)

    def close_tab(self, index: int) -> None:
        if index < 0 or index >= self.count():
            return
        self.removeTab(index)
        self._rebuild_index_map()
        if self.count() == 0:
            self.no_tabs_remaining.emit()
        else:
            active = self._tab_models.get(self.currentIndex())
            self.active_tab_changed.emit(active)

    def _rebuild_index_map(self) -> None:
        new_models: Dict[int, TabModel] = {}
        new_highlighters: Dict[int, SyntaxHighlighter] = {}
        for i in range(self.count()):
            widget = self.widget(i)
            for old_idx, model in self._tab_models.items():
                if self.widget(old_idx) == widget:
                    new_models[i] = model
                    if old_idx in self._highlighters:
                        new_highlighters[i] = self._highlighters[old_idx]
                    break
        self._tab_models = new_models
        self._highlighters = new_highlighters

    def current_editor(self) -> Optional[CodeEditor]:
        widget = self.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def current_model(self) -> Optional[TabModel]:
        return self._tab_models.get(self.currentIndex())

    def editor_at(self, index: int) -> Optional[CodeEditor]:
        widget = self.widget(index)
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def model_at(self, index: int) -> Optional[TabModel]:
        return self._tab_models.get(index)

    def all_models(self) -> List[TabModel]:
        return list(self._tab_models.values())

    def update_tab_title(self, index: int) -> None:
        model = self._tab_models.get(index)
        if model:
            self.setTabText(index, model.display_title)

    def save_current_content_to_model(self) -> None:
        index = self.currentIndex()
        editor = self.current_editor()
        model = self.current_model()
        if editor and model:
            model.content = editor.toPlainText()
            model.cursor_position = editor.textCursor().position()
            model.is_modified = False
            self.setTabText(index, model.display_title)

    def apply_theme(self, theme: str) -> None:
        self._current_theme = theme
        for i in range(self.count()):
            editor = self.editor_at(i)
            if editor:
                editor.set_theme_colors(theme.lower())
            if i in self._highlighters:
                self._highlighters[i].set_theme(theme)

    def find_tab_by_path(self, path: str) -> int:
        for i, model in self._tab_models.items():
            if model.file_path == path:
                return i
        return -1

    def duplicate_tab(self) -> None:
        model = self.current_model()
        editor = self.current_editor()
        if not model or not editor:
            return
        new_model = TabModel(
            file_path=model.file_path,
            title=f"{model.title} (copy)",
            content=editor.toPlainText(),
            encoding=model.encoding,
        )
        self.add_tab(new_model)
