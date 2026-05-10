import sqlite3
import os
from typing import List, Optional, Dict, Any
from core.constants import AppConstants
from utils.logger import get_logger

logger = get_logger("DatabaseManager")


class DatabaseManager:
    _instance: Optional["DatabaseManager"] = None

    def __new__(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection: Optional[sqlite3.Connection] = None
            cls._instance._initialized = False
        return cls._instance

    def initialize(self) -> None:
        if self._initialized:
            return
        os.makedirs(AppConstants.DATA_DIR, exist_ok=True)
        self._connection = sqlite3.connect(AppConstants.DB_PATH, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._create_tables()
        self._initialized = True
        logger.info("Database initialized at %s", AppConstants.DB_PATH)

    def _create_tables(self) -> None:
        assert self._connection
        self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS tabs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                title TEXT NOT NULL DEFAULT 'Untitled',
                content TEXT DEFAULT '',
                cursor_position INTEGER DEFAULT 0,
                scroll_position INTEGER DEFAULT 0,
                is_modified INTEGER DEFAULT 0,
                encoding TEXT DEFAULT 'UTF-8',
                tab_order INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS recent_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                accessed_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                label TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)
        self._connection.commit()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        assert self._connection
        try:
            cursor = self._connection.execute(query, params)
            self._connection.commit()
            return cursor
        except sqlite3.Error as e:
            logger.error("DB error: %s | Query: %s", e, query)
            raise

    def fetchall(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        assert self._connection
        cursor = self._connection.execute(query, params)
        return cursor.fetchall()

    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        assert self._connection
        cursor = self._connection.execute(query, params)
        return cursor.fetchone()

    def save_tab(self, tab_data: Dict[str, Any]) -> int:
        if tab_data.get("id"):
            self.execute(
                """UPDATE tabs SET file_path=?, title=?, content=?, cursor_position=?,
                   scroll_position=?, is_modified=?, encoding=?, tab_order=?,
                   updated_at=datetime('now') WHERE id=?""",
                (
                    tab_data.get("file_path"),
                    tab_data.get("title", "Untitled"),
                    tab_data.get("content", ""),
                    tab_data.get("cursor_position", 0),
                    tab_data.get("scroll_position", 0),
                    int(tab_data.get("is_modified", False)),
                    tab_data.get("encoding", "UTF-8"),
                    tab_data.get("tab_order", 0),
                    tab_data["id"],
                ),
            )
            return tab_data["id"]
        else:
            cursor = self.execute(
                """INSERT INTO tabs (file_path, title, content, cursor_position,
                   scroll_position, is_modified, encoding, tab_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    tab_data.get("file_path"),
                    tab_data.get("title", "Untitled"),
                    tab_data.get("content", ""),
                    tab_data.get("cursor_position", 0),
                    tab_data.get("scroll_position", 0),
                    int(tab_data.get("is_modified", False)),
                    tab_data.get("encoding", "UTF-8"),
                    tab_data.get("tab_order", 0),
                ),
            )
            return cursor.lastrowid or 0

    def get_all_tabs(self) -> List[sqlite3.Row]:
        return self.fetchall("SELECT * FROM tabs ORDER BY tab_order ASC")

    def delete_tab(self, tab_id: int) -> None:
        self.execute("DELETE FROM tabs WHERE id=?", (tab_id,))

    def clear_tabs(self) -> None:
        self.execute("DELETE FROM tabs")

    def add_recent_file(self, path: str) -> None:
        self.execute(
            """INSERT INTO recent_files (file_path, accessed_at) VALUES (?, datetime('now'))
               ON CONFLICT(file_path) DO UPDATE SET accessed_at=datetime('now')""",
            (path,),
        )
        self.execute(
            """DELETE FROM recent_files WHERE id NOT IN (
               SELECT id FROM recent_files ORDER BY accessed_at DESC LIMIT ?)""",
            (AppConstants.MAX_RECENT_FILES,),
        )

    def get_recent_files(self) -> List[str]:
        rows = self.fetchall(
            "SELECT file_path FROM recent_files ORDER BY accessed_at DESC"
        )
        return [row["file_path"] for row in rows if os.path.exists(row["file_path"])]

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
            self._initialized = False
