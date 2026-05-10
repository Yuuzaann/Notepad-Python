from __future__ import annotations
import os
from typing import Optional
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeView, QFileSystemModel, QMenu, QSizePolicy, QWidget,
    QAbstractItemView
)
from PySide6.QtCore import Signal, Qt, QDir, QModelIndex, QPoint, QSortFilterProxyModel
from PySide6.QtGui import QAction, QIcon, QFont


class SidebarWidget(QFrame):
    file_open_requested = Signal(str)
    folder_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumWidth(160)
        self.setMaximumWidth(480)

        self._root_path: Optional[str] = None
        self._fs_model = QFileSystemModel()
        self._fs_model.setRootPath("")
        self._fs_model.setFilter(
            QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot
        )

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(36)
        header.setObjectName("sidebarHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 6, 0)
        header_layout.setSpacing(4)

        title_label = QLabel("EXPLORER")
        title_label.setObjectName("subtitle")
        font = title_label.font()
        font.setPointSize(10)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        title_label.setFont(font)

        self._open_folder_btn = QPushButton("⊕")
        self._open_folder_btn.setFixedSize(24, 24)
        self._open_folder_btn.setToolTip("Open Folder")
        self._open_folder_btn.setObjectName("secondary")
        self._open_folder_btn.setFlat(True)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self._open_folder_btn)

        self._tree_view = QTreeView()
        self._tree_view.setModel(self._fs_model)
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setAnimated(True)
        self._tree_view.setIndentation(16)
        self._tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree_view.setDragEnabled(False)
        self._tree_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        for col in range(1, self._fs_model.columnCount()):
            self._tree_view.hideColumn(col)

        self._empty_label = QLabel("No folder opened\n\nClick ⊕ to open a folder")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setObjectName("subtitle")
        self._empty_label.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(self._empty_label)
        layout.addWidget(self._tree_view)

        self._tree_view.hide()

    def _connect_signals(self) -> None:
        self._open_folder_btn.clicked.connect(self._request_open_folder)
        self._tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self._tree_view.customContextMenuRequested.connect(self._show_context_menu)

    def _request_open_folder(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "Open Folder", os.path.expanduser("~"))
        if path:
            self.set_root_folder(path)

    def set_root_folder(self, path: str) -> None:
        self._root_path = path
        self._fs_model.setRootPath(path)
        index = self._fs_model.index(path)
        self._tree_view.setRootIndex(index)
        self._tree_view.show()
        self._empty_label.hide()
        self.folder_changed.emit(path)

    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        path = self._fs_model.filePath(index)
        if os.path.isfile(path):
            self.file_open_requested.emit(path)
        else:
            if self._tree_view.isExpanded(index):
                self._tree_view.collapse(index)
            else:
                self._tree_view.expand(index)

    def _show_context_menu(self, point: QPoint) -> None:
        index = self._tree_view.indexAt(point)
        if not index.isValid():
            return

        path = self._fs_model.filePath(index)
        menu = QMenu(self)

        if os.path.isfile(path):
            open_action = QAction("Open File", self)
            open_action.triggered.connect(lambda: self.file_open_requested.emit(path))
            menu.addAction(open_action)
            menu.addSeparator()

        reveal_action = QAction("Reveal in File Manager", self)
        reveal_action.triggered.connect(lambda: self._reveal_in_file_manager(path))
        menu.addAction(reveal_action)

        copy_path_action = QAction("Copy Path", self)
        copy_path_action.triggered.connect(lambda: self._copy_path(path))
        menu.addAction(copy_path_action)

        if os.path.isdir(path):
            menu.addSeparator()
            set_root_action = QAction("Set as Root Folder", self)
            set_root_action.triggered.connect(lambda: self.set_root_folder(path))
            menu.addAction(set_root_action)

        menu.exec(self._tree_view.viewport().mapToGlobal(point))

    def _reveal_in_file_manager(self, path: str) -> None:
        import subprocess, sys
        folder = path if os.path.isdir(path) else os.path.dirname(path)
        if sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        elif sys.platform == "win32":
            subprocess.Popen(["explorer", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def _copy_path(self, path: str) -> None:
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(path)

    def collapse_all(self) -> None:
        self._tree_view.collapseAll()

    def expand_all(self) -> None:
        self._tree_view.expandAll()
