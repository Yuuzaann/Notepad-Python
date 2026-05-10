from __future__ import annotations
import os
import re
from typing import Optional, List
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QFileDialog, QMessageBox, QToolBar,
    QLabel, QPushButton, QComboBox, QApplication,
    QMenuBar, QMenu, QSizePolicy, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QSettings
from PySide6.QtGui import (
    QAction, QKeySequence, QFont, QCloseEvent, QIcon,
    QTextCursor, QColor
)

from config.settings import Settings
from core.constants import AppConstants, SUPPORTED_EXTENSIONS
from database.db_manager import DatabaseManager
from models.tab_model import TabModel
from services.file_service import FileService
from services.auto_save_service import AutoSaveService
from themes.theme_manager import ThemeManager
from widgets.tab_widget import EditorTabWidget
from widgets.sidebar import SidebarWidget
from widgets.status_bar import StatusBarWidget
from widgets.search_bar import SearchBar
from ui.toast import show_toast
from ui.welcome_screen import WelcomeScreen
from ui.settings_dialog import SettingsDialog
from utils.logger import get_logger

logger = get_logger("MainWindow")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._settings = Settings()
        self._db = DatabaseManager()
        self._db.initialize()
        self._file_service = FileService()
        self._theme_manager = ThemeManager()
        self._untitled_counter = 0
        self._search_matches: List[tuple] = []
        self._search_match_index = 0
        self._file_watcher_timer = QTimer(self)
        self._watched_mtimes: dict = {}

        self._setup_window()
        self._build_ui()
        self._build_menus()
        self._build_toolbar()
        self._connect_signals()
        self._apply_initial_theme()
        self._setup_auto_save()
        self._restore_session()
        self._start_file_watcher()

    def _setup_window(self) -> None:
        self.setWindowTitle(AppConstants.APP_NAME)
        w = self._settings.get("window_width", 1280)
        h = self._settings.get("window_height", 800)
        x = self._settings.get("window_x", 100)
        y = self._settings.get("window_y", 100)
        self.setGeometry(x, y, w, h)
        if self._settings.get("window_maximized", False):
            self.showMaximized()
        self.setMinimumSize(700, 500)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._search_bar = SearchBar()
        main_layout.addWidget(self._search_bar)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(1)
        main_layout.addWidget(self._splitter)

        self._sidebar = SidebarWidget()
        sidebar_width = self._settings.get("sidebar_width", 240)
        self._sidebar.setFixedWidth(sidebar_width)
        if not self._settings.get("show_sidebar", True):
            self._sidebar.hide()

        self._editor_stack = QStackedWidget()

        self._welcome_screen = WelcomeScreen(
            recent_files=self._db.get_recent_files()
        )
        self._tab_widget = EditorTabWidget()

        self._editor_stack.addWidget(self._welcome_screen)
        self._editor_stack.addWidget(self._tab_widget)
        self._editor_stack.setCurrentWidget(self._welcome_screen)

        self._splitter.addWidget(self._sidebar)
        self._splitter.addWidget(self._editor_stack)
        self._splitter.setStretchFactor(1, 1)

        self._status_bar = StatusBarWidget()
        self.setStatusBar(self._status_bar)

    def _build_menus(self) -> None:
        mb = self.menuBar()

        file_menu = mb.addMenu("File")
        self._add_action(file_menu, "New File", self.new_file, "Ctrl+N")
        self._add_action(file_menu, "Open File...", self.open_file, "Ctrl+O")
        self._add_action(file_menu, "Open Folder...", self.open_folder, "Ctrl+Shift+O")
        file_menu.addSeparator()
        self._add_action(file_menu, "Save", self.save_file, "Ctrl+S")
        self._add_action(file_menu, "Save As...", self.save_file_as, "Ctrl+Shift+S")
        self._add_action(file_menu, "Save All", self.save_all, "Ctrl+Alt+S")
        file_menu.addSeparator()
        self._recent_menu = file_menu.addMenu("Recent Files")
        self._populate_recent_menu()
        file_menu.addSeparator()
        self._add_action(file_menu, "Close Tab", self.close_current_tab, "Ctrl+W")
        self._add_action(file_menu, "Exit", self.close, "Alt+F4")

        edit_menu = mb.addMenu("Edit")
        self._add_action(edit_menu, "Undo", self._undo, "Ctrl+Z")
        self._add_action(edit_menu, "Redo", self._redo, "Ctrl+Y")
        edit_menu.addSeparator()
        self._add_action(edit_menu, "Cut", self._cut, "Ctrl+X")
        self._add_action(edit_menu, "Copy", self._copy, "Ctrl+C")
        self._add_action(edit_menu, "Paste", self._paste, "Ctrl+V")
        self._add_action(edit_menu, "Select All", self._select_all, "Ctrl+A")
        edit_menu.addSeparator()
        self._add_action(edit_menu, "Find / Replace", self._toggle_search, "Ctrl+F")
        edit_menu.addSeparator()
        self._add_action(edit_menu, "Duplicate Tab", self._tab_widget.duplicate_tab)
        self._add_action(edit_menu, "Indent Selection", self._indent)
        self._add_action(edit_menu, "Unindent Selection", self._unindent)

        view_menu = mb.addMenu("View")
        self._add_action(view_menu, "Toggle Sidebar", self._toggle_sidebar, "Ctrl+B")
        self._add_action(view_menu, "Toggle Toolbar", self._toggle_toolbar)
        view_menu.addSeparator()
        self._add_action(view_menu, "Zoom In", self._zoom_in, "Ctrl+=")
        self._add_action(view_menu, "Zoom Out", self._zoom_out, "Ctrl+-")
        self._add_action(view_menu, "Reset Zoom", self._zoom_reset, "Ctrl+0")
        view_menu.addSeparator()
        theme_menu = view_menu.addMenu("Theme")
        for t in self._theme_manager.available_themes:
            action = QAction(t, self)
            action.triggered.connect(lambda checked, name=t: self._apply_theme(name))
            theme_menu.addAction(action)

        tools_menu = mb.addMenu("Tools")
        self._add_action(tools_menu, "Settings...", self._open_settings, "Ctrl+,")

        help_menu = mb.addMenu("Help")
        self._add_action(help_menu, f"About {AppConstants.APP_NAME}", self._show_about)

    def _add_action(self, menu: QMenu, text: str, slot, shortcut: str = "") -> QAction:
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _build_toolbar(self) -> None:
        self._toolbar = self.addToolBar("Main Toolbar")
        self._toolbar.setMovable(False)
        self._toolbar.setIconSize(QSize(16, 16))
        self._toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        def tb_action(text: str, slot, shortcut: str = "", tooltip: str = "") -> QAction:
            act = QAction(text, self)
            act.triggered.connect(slot)
            if shortcut:
                act.setShortcut(QKeySequence(shortcut))
            if tooltip:
                act.setToolTip(tooltip)
            self._toolbar.addAction(act)
            return act

        tb_action("✦ New", self.new_file, "Ctrl+N", "New File (Ctrl+N)")
        tb_action("📂 Open", self.open_file, "Ctrl+O", "Open File (Ctrl+O)")
        tb_action("💾 Save", self.save_file, "Ctrl+S", "Save (Ctrl+S)")
        self._toolbar.addSeparator()
        tb_action("↩ Undo", self._undo, "Ctrl+Z", "Undo (Ctrl+Z)")
        tb_action("↪ Redo", self._redo, "Ctrl+Y", "Redo (Ctrl+Y)")
        self._toolbar.addSeparator()
        tb_action("🔍 Find", self._toggle_search, "Ctrl+F", "Find/Replace (Ctrl+F)")
        self._toolbar.addSeparator()
        tb_action("A+ Zoom In", self._zoom_in, "Ctrl+=", "Zoom In")
        tb_action("A- Zoom Out", self._zoom_out, "Ctrl+-", "Zoom Out")
        self._toolbar.addSeparator()
        tb_action("⚙ Settings", self._open_settings, "Ctrl+,", "Settings")

        if not self._settings.get("show_toolbar", True):
            self._toolbar.hide()

    def _connect_signals(self) -> None:
        self._tab_widget.active_tab_changed.connect(self._on_active_tab_changed)
        self._tab_widget.no_tabs_remaining.connect(self._on_no_tabs)
        self._tab_widget.tab_modified_changed.connect(self._on_tab_modified)

        self._sidebar.file_open_requested.connect(self._open_file_from_path)
        self._sidebar.folder_changed.connect(self._on_folder_changed)

        self._welcome_screen.new_file_requested.connect(self.new_file)
        self._welcome_screen.open_file_requested.connect(self.open_file)
        self._welcome_screen.open_folder_requested.connect(self.open_folder)
        self._welcome_screen.recent_file_requested.connect(self._open_file_from_path)

        self._search_bar.search_requested.connect(self._do_search)
        self._search_bar.replace_requested.connect(self._do_replace)
        self._search_bar.replace_all_requested.connect(self._do_replace_all)
        self._search_bar.navigate_next.connect(self._search_next)
        self._search_bar.navigate_prev.connect(self._search_prev)
        self._search_bar.closed.connect(self._on_search_closed)

        self._file_watcher_timer.timeout.connect(self._check_external_changes)

    def _apply_initial_theme(self) -> None:
        theme = self._settings.get("theme", "Dark")
        self._theme_manager.apply_theme(theme, QApplication.instance())
        self._tab_widget.apply_theme(theme)

    def _apply_theme(self, theme: str) -> None:
        self._settings.set("theme", theme)
        self._settings.save()
        self._theme_manager.apply_theme(theme, QApplication.instance())
        self._tab_widget.apply_theme(theme)
        show_toast(f"Theme: {theme}", self)

    def _setup_auto_save(self) -> None:
        self._auto_save_service = AutoSaveService(self._auto_save_all)
        if self._settings.get("auto_save", True):
            interval = self._settings.get("auto_save_interval", AppConstants.AUTO_SAVE_INTERVAL)
            self._auto_save_service.start(interval)

    def _restore_session(self) -> None:
        if not self._settings.get("restore_tabs", True):
            return
        rows = self._db.get_all_tabs()
        if not rows:
            return
        for row in rows:
            model = TabModel.from_dict(dict(row))
            if model.file_path and os.path.exists(model.file_path):
                try:
                    content, enc = self._file_service.read_file(model.file_path)
                    model.content = content
                    model.encoding = enc
                    model.is_modified = False
                except OSError:
                    pass
            self._tab_widget.add_tab(model)
        self._editor_stack.setCurrentWidget(self._tab_widget)
        saved_index = self._settings.get("active_tab_index", 0)
        if 0 <= saved_index < self._tab_widget.count():
            self._tab_widget.setCurrentIndex(saved_index)

    def _start_file_watcher(self) -> None:
        self._file_watcher_timer.start(AppConstants.FILE_WATCH_INTERVAL)

    def _check_external_changes(self) -> None:
        for i in range(self._tab_widget.count()):
            model = self._tab_widget.model_at(i)
            if model and model.file_path and os.path.exists(model.file_path):
                mtime = os.path.getmtime(model.file_path)
                if model.file_path in self._watched_mtimes:
                    if mtime > self._watched_mtimes[model.file_path] + 0.5:
                        self._watched_mtimes[model.file_path] = mtime
                        self._prompt_reload(i, model)
                else:
                    self._watched_mtimes[model.file_path] = mtime

    def _prompt_reload(self, index: int, model: TabModel) -> None:
        reply = QMessageBox.question(
            self,
            "File Changed",
            f'"{model.title}" was changed externally.\nReload it?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                content, enc = self._file_service.read_file(model.file_path)
                editor = self._tab_widget.editor_at(index)
                if editor:
                    editor.setPlainText(content)
                model.content = content
                model.encoding = enc
                model.is_modified = False
                self._tab_widget.update_tab_title(index)
            except OSError:
                pass

    def new_file(self) -> None:
        self._untitled_counter += 1
        model = TabModel(
            title=f"Untitled-{self._untitled_counter}",
            content="",
            tab_order=self._tab_widget.count(),
        )
        self._tab_widget.add_tab(model)
        self._editor_stack.setCurrentWidget(self._tab_widget)

    def open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", os.path.expanduser("~"),
            "All Files (*);;Text Files (*.txt);;Python (*.py);;JavaScript (*.js)"
        )
        if path:
            self._open_file_from_path(path)

    def _open_file_from_path(self, path: str) -> None:
        existing = self._tab_widget.find_tab_by_path(path)
        if existing >= 0:
            self._tab_widget.setCurrentIndex(existing)
            return

        try:
            content, encoding = self._file_service.read_file(path)
        except (OSError, UnicodeDecodeError) as e:
            QMessageBox.critical(self, "Error", f"Cannot open file:\n{e}")
            return

        import os as _os
        filename = _os.path.basename(path)
        model = TabModel(
            file_path=path,
            title=filename,
            content=content,
            encoding=encoding,
            tab_order=self._tab_widget.count(),
        )
        self._tab_widget.add_tab(model)
        self._editor_stack.setCurrentWidget(self._tab_widget)
        self._db.add_recent_file(path)
        self._settings.add_recent_file(path)
        self._settings.save()
        self._populate_recent_menu()
        self._watched_mtimes[path] = os.path.getmtime(path)
        show_toast(f"Opened: {filename}", self)

    def open_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Open Folder", os.path.expanduser("~"))
        if path:
            self._sidebar.set_root_folder(path)
            if not self._settings.get("show_sidebar", True):
                self._toggle_sidebar()
            self._settings.set("last_folder", path)
            self._settings.save()

    def save_file(self) -> bool:
        model = self._tab_widget.current_model()
        editor = self._tab_widget.current_editor()
        if not model or not editor:
            return False

        if not model.file_path:
            return self.save_file_as()

        content = editor.toPlainText()
        if self._settings.get("backup_enabled", True) and model.file_path:
            self._file_service.create_backup(model.file_path, content)

        success = self._file_service.write_file(model.file_path, content, model.encoding)
        if success:
            model.content = content
            model.is_modified = False
            self._tab_widget.update_tab_title(self._tab_widget.currentIndex())
            self._watched_mtimes[model.file_path] = os.path.getmtime(model.file_path)
            self._save_tab_to_db(self._tab_widget.currentIndex(), model)
            show_toast(f"Saved: {model.title}", self)
        else:
            QMessageBox.critical(self, "Error", f"Failed to save: {model.file_path}")
        return success

    def save_file_as(self) -> bool:
        model = self._tab_widget.current_model()
        editor = self._tab_widget.current_editor()
        if not model or not editor:
            return False

        default = model.file_path or os.path.join(os.path.expanduser("~"), model.title)
        path, _ = QFileDialog.getSaveFileName(self, "Save As", default, "All Files (*)")
        if not path:
            return False

        model.file_path = path
        model.title = os.path.basename(path)
        model.encoding = self._settings.get("encoding", "UTF-8")

        content = editor.toPlainText()
        success = self._file_service.write_file(path, content, model.encoding)
        if success:
            model.content = content
            model.is_modified = False
            self._tab_widget.update_tab_title(self._tab_widget.currentIndex())
            self._db.add_recent_file(path)
            self._settings.add_recent_file(path)
            self._settings.save()
            self._populate_recent_menu()
            self._watched_mtimes[path] = os.path.getmtime(path)
            show_toast(f"Saved: {model.title}", self)
        return success

    def save_all(self) -> None:
        current = self._tab_widget.currentIndex()
        for i in range(self._tab_widget.count()):
            self._tab_widget.setCurrentIndex(i)
            self.save_file()
        self._tab_widget.setCurrentIndex(current)

    def _auto_save_all(self) -> None:
        for i in range(self._tab_widget.count()):
            model = self._tab_widget.model_at(i)
            editor = self._tab_widget.editor_at(i)
            if model and editor and model.is_modified and model.file_path:
                content = editor.toPlainText()
                self._file_service.write_file(model.file_path, content, model.encoding)
                self._file_service.save_temp(i, content)
                model.is_modified = False
                self._tab_widget.update_tab_title(i)
        self._persist_session()

    def close_current_tab(self) -> None:
        index = self._tab_widget.currentIndex()
        model = self._tab_widget.current_model()
        editor = self._tab_widget.current_editor()
        if not model:
            return
        if model.is_modified and editor:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f'"{model.title}" has unsaved changes. Save before closing?',
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        if model.id:
            self._db.delete_tab(model.id)
        self._tab_widget.close_tab(index)

    def _on_no_tabs(self) -> None:
        self._welcome_screen._recent_files = self._db.get_recent_files()
        self._welcome_screen._build_ui()
        self._editor_stack.setCurrentWidget(self._welcome_screen)
        self._status_bar.update_position(1, 1)
        self._status_bar.update_stats(0, 0)
        self.setWindowTitle(AppConstants.APP_NAME)

    def _on_active_tab_changed(self, model: Optional[TabModel]) -> None:
        if not model:
            return
        title = f"{model.display_title} — {AppConstants.APP_NAME}"
        self.setWindowTitle(title)
        editor = self._tab_widget.current_editor()
        if editor:
            stats = editor.get_stats()
            self._status_bar.update_position(stats["line"], stats["col"])
            self._status_bar.update_stats(stats["words"], stats["chars"])
            self._status_bar.update_zoom(editor.zoom_level)
            editor.cursor_position_changed_signal.connect(
                lambda l, c: self._status_bar.update_position(l, c)
            )
            editor.content_changed.connect(self._on_editor_content_changed)
        if model.file_path:
            ext = os.path.splitext(model.file_path)[1].lower()
            self._status_bar.update_filetype(SUPPORTED_EXTENSIONS.get(ext, "Plain Text"))
        else:
            self._status_bar.update_filetype("Plain Text")
        self._status_bar.update_encoding(model.encoding)

    def _on_editor_content_changed(self) -> None:
        editor = self._tab_widget.current_editor()
        if editor:
            stats = editor.get_stats()
            self._status_bar.update_stats(stats["words"], stats["chars"])

    def _on_tab_modified(self, index: int, modified: bool) -> None:
        model = self._tab_widget.model_at(index)
        if model and index == self._tab_widget.currentIndex():
            self.setWindowTitle(f"{model.display_title} — {AppConstants.APP_NAME}")

    def _on_folder_changed(self, path: str) -> None:
        self._settings.set("last_folder", path)
        self._settings.save()

    def _toggle_sidebar(self) -> None:
        if self._sidebar.isVisible():
            self._sidebar.hide()
            self._settings.set("show_sidebar", False)
        else:
            self._sidebar.show()
            self._settings.set("show_sidebar", True)
        self._settings.save()

    def _toggle_toolbar(self) -> None:
        if self._toolbar.isVisible():
            self._toolbar.hide()
            self._settings.set("show_toolbar", False)
        else:
            self._toolbar.show()
            self._settings.set("show_toolbar", True)
        self._settings.save()

    def _toggle_search(self) -> None:
        if self._search_bar.isVisible():
            self._search_bar.close_bar()
        else:
            editor = self._tab_widget.current_editor()
            selected = editor.textCursor().selectedText() if editor else ""
            self._search_bar.open_bar(selected)

    def _on_search_closed(self) -> None:
        editor = self._tab_widget.current_editor()
        if editor:
            editor.clear_search_highlights()
        self._search_matches = []

    def _do_search(self, text: str, match_case: bool, use_regex: bool) -> None:
        editor = self._tab_widget.current_editor()
        if not editor or not text:
            editor and editor.clear_search_highlights()
            self._search_bar.update_match_count(0, 0)
            return

        content = editor.toPlainText()
        flags = 0 if match_case else re.IGNORECASE

        try:
            pattern = text if use_regex else re.escape(text)
            matches = list(re.finditer(pattern, content, flags))
        except re.error:
            return

        self._search_matches = [(m.start(), len(m.group())) for m in matches]
        editor.set_search_highlights(self._search_matches)
        self._search_match_index = 0
        self._search_bar.update_match_count(
            min(1, len(self._search_matches)), len(self._search_matches)
        )
        if self._search_matches:
            self._goto_match(0)

    def _goto_match(self, index: int) -> None:
        if not self._search_matches:
            return
        editor = self._tab_widget.current_editor()
        if not editor:
            return
        start, length = self._search_matches[index]
        cursor = editor.textCursor()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, length)
        editor.setTextCursor(cursor)
        editor.ensureCursorVisible()
        self._search_bar.update_match_count(index + 1, len(self._search_matches))

    def _search_next(self) -> None:
        if not self._search_matches:
            self._do_search(
                self._search_bar.find_text,
                self._search_bar.match_case,
                self._search_bar.use_regex,
            )
            return
        self._search_match_index = (self._search_match_index + 1) % len(self._search_matches)
        self._goto_match(self._search_match_index)

    def _search_prev(self) -> None:
        if not self._search_matches:
            return
        self._search_match_index = (self._search_match_index - 1) % len(self._search_matches)
        self._goto_match(self._search_match_index)

    def _do_replace(self, find: str, replace: str, match_case: bool, use_regex: bool) -> None:
        editor = self._tab_widget.current_editor()
        if not editor or not find:
            return
        cursor = editor.textCursor()
        selected = cursor.selectedText()
        flags = 0 if match_case else re.IGNORECASE
        try:
            pattern = find if use_regex else re.escape(find)
            if re.fullmatch(pattern, selected, flags):
                cursor.insertText(replace)
        except re.error:
            pass
        self._search_next()

    def _do_replace_all(self, find: str, replace: str, match_case: bool, use_regex: bool) -> None:
        editor = self._tab_widget.current_editor()
        if not editor or not find:
            return
        content = editor.toPlainText()
        flags = 0 if match_case else re.IGNORECASE
        try:
            pattern = find if use_regex else re.escape(find)
            new_content, count = re.subn(pattern, replace, content, flags=flags)
            if count > 0:
                editor.setPlainText(new_content)
                show_toast(f"Replaced {count} occurrence(s)", self)
        except re.error as e:
            show_toast(f"Regex error: {e}", self)

    def _undo(self) -> None:
        e = self._tab_widget.current_editor()
        e and e.undo()

    def _redo(self) -> None:
        e = self._tab_widget.current_editor()
        e and e.redo()

    def _cut(self) -> None:
        e = self._tab_widget.current_editor()
        e and e.cut()

    def _copy(self) -> None:
        e = self._tab_widget.current_editor()
        e and e.copy()

    def _paste(self) -> None:
        e = self._tab_widget.current_editor()
        e and e.paste()

    def _select_all(self) -> None:
        e = self._tab_widget.current_editor()
        e and e.selectAll()

    def _indent(self) -> None:
        e = self._tab_widget.current_editor()
        if e:
            from PySide6.QtGui import QKeyEvent
            from PySide6.QtCore import Qt
            e._indent_selection()

    def _unindent(self) -> None:
        e = self._tab_widget.current_editor()
        if e:
            e._unindent_selection()

    def _zoom_in(self) -> None:
        e = self._tab_widget.current_editor()
        if e:
            e.zoom_in()
            self._status_bar.update_zoom(e.zoom_level)

    def _zoom_out(self) -> None:
        e = self._tab_widget.current_editor()
        if e:
            e.zoom_out()
            self._status_bar.update_zoom(e.zoom_level)

    def _zoom_reset(self) -> None:
        e = self._tab_widget.current_editor()
        if e:
            e.reset_zoom()
            self._status_bar.update_zoom(e.zoom_level)

    def _populate_recent_menu(self) -> None:
        self._recent_menu.clear()
        recent = self._db.get_recent_files()
        if not recent:
            no_action = QAction("No recent files", self)
            no_action.setEnabled(False)
            self._recent_menu.addAction(no_action)
            return
        for path in recent:
            action = QAction(os.path.basename(path), self)
            action.setToolTip(path)
            action.triggered.connect(lambda checked, p=path: self._open_file_from_path(p))
            self._recent_menu.addAction(action)
        self._recent_menu.addSeparator()
        clear_action = QAction("Clear Recent Files", self)
        clear_action.triggered.connect(self._clear_recent)
        self._recent_menu.addAction(clear_action)

    def _clear_recent(self) -> None:
        self._db.execute("DELETE FROM recent_files")
        self._populate_recent_menu()

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self)
        dialog.theme_changed.connect(lambda t: self._tab_widget.apply_theme(t))
        dialog.settings_applied.connect(self._on_settings_applied)
        dialog.exec()

    def _on_settings_applied(self) -> None:
        self._apply_theme(self._settings.get("theme", "Dark"))
        for i in range(self._tab_widget.count()):
            editor = self._tab_widget.editor_at(i)
            if editor:
                editor.set_font_size(self._settings.get("font_size", 13))
                editor.set_tab_size(self._settings.get("tab_size", 4))
                editor.set_use_spaces(self._settings.get("use_spaces", True))
        if self._settings.get("auto_save", True):
            interval = self._settings.get("auto_save_interval", AppConstants.AUTO_SAVE_INTERVAL)
            self._auto_save_service.start(interval)
        else:
            self._auto_save_service.stop()
        show_toast("Settings applied", self)

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            f"About {AppConstants.APP_NAME}",
            f"<h2>{AppConstants.APP_NAME}</h2>"
            f"<p>Version {AppConstants.APP_VERSION}</p>"
            f"<p>A modern, professional code editor built with Python and PySide6.</p>"
            f"<p>Features: Multi-tab editing, syntax highlighting, themes, "
            f"find/replace, file explorer, and more.</p>",
        )

    def _persist_session(self) -> None:
        if not self._settings.get("restore_tabs", True):
            return
        self._db.clear_tabs()
        for i in range(self._tab_widget.count()):
            model = self._tab_widget.model_at(i)
            editor = self._tab_widget.editor_at(i)
            if model and editor:
                model.content = editor.toPlainText()
                model.cursor_position = editor.textCursor().position()
                model.tab_order = i
                model.id = self._db.save_tab(model.to_dict())
        self._settings.set("active_tab_index", self._tab_widget.currentIndex())
        self._settings.save()

    def _save_tab_to_db(self, index: int, model: TabModel) -> None:
        model.id = self._db.save_tab(model.to_dict())

    def closeEvent(self, event: QCloseEvent) -> None:
        unsaved = []
        for i in range(self._tab_widget.count()):
            model = self._tab_widget.model_at(i)
            editor = self._tab_widget.editor_at(i)
            if model and editor and model.is_modified:
                unsaved.append((i, model))

        if unsaved:
            names = "\n".join(f"  • {m.title}" for _, m in unsaved)
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"You have unsaved changes in:\n{names}\n\nSave all before exiting?",
                QMessageBox.StandardButton.SaveAll
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            if reply == QMessageBox.StandardButton.SaveAll:
                self.save_all()

        self._auto_save_service.stop()
        self._persist_session()
        geo = self.geometry()
        self._settings.set("window_width", geo.width())
        self._settings.set("window_height", geo.height())
        self._settings.set("window_x", geo.x())
        self._settings.set("window_y", geo.y())
        self._settings.set("window_maximized", self.isMaximized())
        self._settings.save()
        self._db.close()
        event.accept()
