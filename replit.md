# Modern Notepad Pro

A production-grade desktop notepad/code editor built with Python and PySide6 — inspired by VSCode, Sublime Text, and Windows Notepad.

## Run & Operate

- `cd modern_notepad && python3 main.py` — launch the desktop app
- `pip install PySide6 Pygments` — install dependencies (already installed via Replit)
- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9 (existing workspace)
- **Desktop App**: Python 3.11, PySide6 6.11, Pygments 2.20, SQLite
- API: Express 5
- DB: PostgreSQL + Drizzle ORM (workspace); SQLite (desktop app)

## Where things live

- `modern_notepad/` — the entire Python desktop application
  - `main.py` — entry point
  - `core/constants.py` — all app constants, paths, supported file types
  - `config/settings.py` — JSON-based settings singleton (persisted in ~/.modern_notepad/)
  - `database/db_manager.py` — SQLite manager (tabs, recent files, bookmarks)
  - `models/` — Tab and File data models
  - `services/` — FileService (read/write/backup) and AutoSaveService (QTimer-based)
  - `utils/syntax_highlighter.py` — Pygments-powered QSyntaxHighlighter for 25+ languages
  - `themes/*.qss` — QSS stylesheets for Dark, Light, Dracula, Midnight themes
  - `widgets/` — CodeEditor, EditorTabWidget, SidebarWidget, StatusBarWidget, SearchBar
  - `ui/` — MainWindow, WelcomeScreen, SettingsDialog, Toast notifications

## Architecture decisions

- **Clean Architecture with singletons**: Settings and DatabaseManager are singletons for cross-widget access without prop drilling.
- **QSS-based theming**: Each theme is a standalone `.qss` file loaded at runtime; switching is instant with no restart.
- **Pygments + QSyntaxHighlighter**: Language detection is automatic from file extension via Pygments; highlighting runs per-block for performance.
- **SQLite session persistence**: Open tabs (with cursor position, scroll, content, and file path) are saved to SQLite and restored on next launch.
- **File watcher via QTimer**: External file changes are detected every 2 seconds and the user is prompted to reload.

## Product

Modern Notepad Pro features:
- **Multi-tab editor** with drag-reorder, close on middle-click, unsaved indicators, duplicate tab
- **Syntax highlighting** for Python, JS, TS, HTML, CSS, JSON, SQL, Java, Go, Rust, and 15+ more
- **Line numbers**, current-line highlight, auto-indent, bracket pairing
- **Search & replace** with regex support, match-case, real-time highlights, navigate next/prev
- **Sidebar file explorer** with tree view, context menu, expand/collapse
- **4 themes**: Dark (VSCode-inspired), Light, Dracula, Midnight
- **Status bar**: line/column, word count, char count, encoding, file type, zoom %
- **Auto-save** every 30 seconds (configurable), file backup before save
- **Session restore**: remembers open tabs between restarts
- **Settings dialog**: theme, font size, tab size, word wrap, encoding, and more
- **Toast notifications**: lightweight animated feedback for all actions
- **Welcome screen**: quick actions + recent file list

## User preferences

- Stack: Python 3.12+, PySide6, SQLite, QSS, Clean Architecture (no Tkinter/Kivy/PyQt5)
- Architecture: fully modular — no monolithic files, separated UI/logic/data layers

## Gotchas

- PySide6 requires a display server (X11 or Wayland); launching in a headless environment will fail
- Settings are stored in `~/.modern_notepad/settings.json`; DB in `~/.modern_notepad/notepad.db`
- Backups are stored in `~/.modern_notepad/backups/` (last 5 per file)
- Run `python3 main.py` from inside the `modern_notepad/` directory (not the workspace root)

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
