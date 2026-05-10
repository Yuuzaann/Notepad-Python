import os

APP_NAME = "Modern Notepad Pro"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Modern Notepad Pro Team"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.expanduser("~"), ".modern_notepad")
DB_PATH = os.path.join(DATA_DIR, "notepad.db")
LOG_DIR = os.path.join(BASE_DIR, "logs")
TEMP_DIR = os.path.join(DATA_DIR, "temp")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

DEFAULT_FONT_FAMILY = "Consolas"
DEFAULT_FONT_SIZE = 13
DEFAULT_TAB_SIZE = 4
DEFAULT_THEME = "Dark"
DEFAULT_ENCODING = "UTF-8"

MAX_RECENT_FILES = 15
AUTO_SAVE_INTERVAL = 30000
FILE_WATCH_INTERVAL = 2000
BACKUP_INTERVAL = 60000

SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".html": "HTML",
    ".css": "CSS",
    ".json": "JSON",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown",
    ".txt": "Plain Text",
    ".sh": "Shell",
    ".bash": "Bash",
    ".sql": "SQL",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C Header",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".r": "R",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "Config",
    ".env": "Environment",
}


class AppConstants:
    APP_NAME = APP_NAME
    APP_VERSION = APP_VERSION
    APP_AUTHOR = APP_AUTHOR
    BASE_DIR = BASE_DIR
    DATA_DIR = DATA_DIR
    DB_PATH = DB_PATH
    LOG_DIR = LOG_DIR
    TEMP_DIR = TEMP_DIR
    BACKUP_DIR = BACKUP_DIR
    DEFAULT_FONT_FAMILY = DEFAULT_FONT_FAMILY
    DEFAULT_FONT_SIZE = DEFAULT_FONT_SIZE
    DEFAULT_TAB_SIZE = DEFAULT_TAB_SIZE
    DEFAULT_THEME = DEFAULT_THEME
    DEFAULT_ENCODING = DEFAULT_ENCODING
    MAX_RECENT_FILES = MAX_RECENT_FILES
    AUTO_SAVE_INTERVAL = AUTO_SAVE_INTERVAL
    FILE_WATCH_INTERVAL = FILE_WATCH_INTERVAL
    BACKUP_INTERVAL = BACKUP_INTERVAL
    SUPPORTED_EXTENSIONS = SUPPORTED_EXTENSIONS
