# Modern Notepad Pro

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.11-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)

**A professional, production-grade desktop code editor built with Python and PySide6.**  
Inspired by VSCode, Sublime Text, and Windows Notepad — reimagined with clean architecture.

</div>

---

## Features

### Multi-Tab Editor
- Open multiple files simultaneously in a tabbed interface
- Drag and reorder tabs freely
- Close tabs with middle-click or the × button
- Duplicate any tab in one click
- Unsaved file indicator (`*`) in tab title
- Full session restore — tabs reopen automatically on next launch

### Advanced Text Editor
- **Syntax highlighting** for 25+ languages powered by Pygments:  
  Python, JavaScript, TypeScript, HTML, CSS, JSON, SQL, Java, Go, Rust, C/C++, C#, PHP, Ruby, Swift, Kotlin, YAML, TOML, Markdown, and more
- **Line numbers** with current-line highlight
- **Auto indentation** and smart Tab/Space handling
- **Bracket pairing** — wraps selected text in `()`, `[]`, `{}`
- **Zoom in/out** with `Ctrl+Scroll` or `Ctrl+=/–`
- Full undo/redo history

### Find & Replace
- Real-time search highlights as you type
- Navigate matches with `↑` / `↓` buttons or `Enter` / `Shift+Enter`
- Replace single or all occurrences
- **Regex support** and **match-case** toggle
- Match counter (`3/14`)

### File Explorer Sidebar
- Tree view of any folder on your system
- Right-click context menu: open, copy path, reveal in file manager, set as root
- Expand/collapse directories
- Animated toggle with `Ctrl+B`

### Theme System
| Theme | Description |
|---|---|
| **Dark** | VSCode-inspired dark theme |
| **Light** | Clean, minimal light theme |
| **Dracula** | Classic Dracula color scheme |
| **Midnight** | Deep blue dark theme |

All themes are modular `.qss` files — switch instantly with no restart.

### File System
- New, Open, Save, Save As, Save All
- **Auto-save** every 30 seconds (configurable)
- **File backup** before every save (last 5 backups kept per file)
- **External change detection** — prompts to reload if a file is modified outside the app
- Recent files list with quick access

### Status Bar
Real-time display of: line/column position · word count · character count · encoding · file type · zoom level

### Settings
Persistent settings for: theme · font size · tab size · spaces vs tabs · auto-save · word wrap · line numbers · encoding · session restore · and more.

---

## Screenshots

> *(Coming soon — run the app to see it in action)*

---

## Installation

### Requirements
- Python 3.11 or newer
- A display server (X11, Wayland, or Windows/macOS native)

### Install dependencies

```bash
pip install PySide6 Pygments
```

> **Note:** Pygments is optional. The app runs without it, but syntax highlighting will be disabled.

### Run

```bash
cd modern_notepad
python main.py
```

---

## Project Structure

```
modern_notepad/
│
├── main.py                   # Entry point
├── requirements.txt          # Python dependencies
│
├── config/
│   └── settings.py           # JSON settings singleton (~/.modern_notepad/settings.json)
│
├── core/
│   └── constants.py          # App-wide constants, paths, supported extensions
│
├── database/
│   └── db_manager.py         # SQLite manager — tabs, recent files, bookmarks
│
├── models/
│   ├── tab_model.py          # Tab data model
│   └── file_model.py         # File data model
│
├── services/
│   ├── file_service.py       # File read/write, backup, temp files
│   └── auto_save_service.py  # QTimer-based auto-save service
│
├── utils/
│   ├── logger.py             # Rotating file logger
│   └── syntax_highlighter.py # Pygments-powered QSyntaxHighlighter
│
├── themes/
│   ├── theme_manager.py      # Theme loader and switcher
│   ├── dark_theme.qss        # Dark theme stylesheet
│   ├── light_theme.qss       # Light theme stylesheet
│   ├── dracula_theme.qss     # Dracula theme stylesheet
│   └── midnight_theme.qss    # Midnight theme stylesheet
│
├── widgets/
│   ├── editor.py             # CodeEditor (QPlainTextEdit subclass)
│   ├── line_number_area.py   # Line number gutter widget
│   ├── tab_widget.py         # Multi-tab editor container
│   ├── sidebar.py            # File explorer sidebar
│   ├── status_bar.py         # Status bar widget
│   └── search_bar.py         # Find & Replace bar
│
├── ui/
│   ├── main_window.py        # Main application window
│   ├── welcome_screen.py     # Welcome screen with quick actions
│   ├── settings_dialog.py    # Settings dialog
│   └── toast.py              # Animated toast notifications
│
├── assets/
│   └── icons/                # App icons
│
├── logs/                     # Rotating log files (auto-created)
└── tests/                    # Unit tests
```

---

## Architecture

Modern Notepad Pro follows **Clean Architecture** principles:

- **UI Layer** (`ui/`, `widgets/`) — Pure presentation, no business logic
- **Service Layer** (`services/`) — File I/O, auto-save, backup logic
- **Data Layer** (`database/`, `models/`) — SQLite persistence, data models
- **Config Layer** (`config/`) — Settings singleton with JSON persistence
- **Theme Layer** (`themes/`) — Modular QSS stylesheets, runtime switching
- **Utility Layer** (`utils/`) — Logging, syntax highlighting

**Key design decisions:**
- `Settings` and `DatabaseManager` are singletons — accessible anywhere without prop drilling
- Each theme is a self-contained `.qss` file, making it easy to add new themes
- Syntax highlighting runs per block via `QSyntaxHighlighter` for real-time performance
- Session state (tabs, cursor positions, scroll) is persisted to SQLite and restored on launch
- File watcher runs on a `QTimer` every 2 seconds — no filesystem event daemon required

---

## Data & Storage

All user data is stored in `~/.modern_notepad/`:

| Path | Contents |
|---|---|
| `settings.json` | All user preferences |
| `notepad.db` | Open tabs, recent files, bookmarks (SQLite) |
| `backups/` | Timestamped file backups (last 5 per file) |
| `temp/` | Temporary tab content |

---

## Keyboard Shortcuts

| Action | Shortcut |
|---|---|
| New file | `Ctrl+N` |
| Open file | `Ctrl+O` |
| Open folder | `Ctrl+Shift+O` |
| Save | `Ctrl+S` |
| Save As | `Ctrl+Shift+S` |
| Save All | `Ctrl+Alt+S` |
| Close tab | `Ctrl+W` |
| Find / Replace | `Ctrl+F` |
| Toggle sidebar | `Ctrl+B` |
| Zoom in | `Ctrl+=` |
| Zoom out | `Ctrl+-` |
| Reset zoom | `Ctrl+0` |
| Settings | `Ctrl+,` |
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Y` |

---

## Tech Stack

| Component | Technology |
|---|---|
| GUI Framework | PySide6 (Qt 6) |
| Syntax Highlighting | Pygments 2.20 |
| Database | SQLite (via Python `sqlite3`) |
| Styling | Qt Style Sheets (QSS) |
| Language | Python 3.11+ |
| Architecture | Clean Architecture / MVC |

---

## Contributing

Contributions are welcome. To add a new theme:

1. Create `themes/yourtheme_theme.qss` following the existing QSS structure
2. Add the theme name to `AVAILABLE_THEMES` in `themes/theme_manager.py`
3. Done — it will appear automatically in the Theme menu and Settings dialog

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with Python & PySide6
</div>
