import json
import os
from typing import Any, Dict, List, Optional
from core.constants import AppConstants


class Settings:
    _instance: Optional["Settings"] = None
    _settings_file: str = os.path.join(AppConstants.DATA_DIR, "settings.json")

    _defaults: Dict[str, Any] = {
        "theme": AppConstants.DEFAULT_THEME,
        "font_family": AppConstants.DEFAULT_FONT_FAMILY,
        "font_size": AppConstants.DEFAULT_FONT_SIZE,
        "tab_size": AppConstants.DEFAULT_TAB_SIZE,
        "use_spaces": True,
        "auto_save": True,
        "auto_save_interval": AppConstants.AUTO_SAVE_INTERVAL,
        "show_line_numbers": True,
        "highlight_current_line": True,
        "word_wrap": False,
        "show_minimap": True,
        "show_sidebar": True,
        "sidebar_width": 240,
        "window_width": 1280,
        "window_height": 800,
        "window_maximized": False,
        "window_x": 100,
        "window_y": 100,
        "recent_files": [],
        "last_folder": "",
        "encoding": AppConstants.DEFAULT_ENCODING,
        "zoom_level": 100,
        "restore_tabs": True,
        "last_tabs": [],
        "active_tab_index": 0,
        "show_toolbar": True,
        "backup_enabled": True,
        "match_brackets": True,
        "auto_indent": True,
    }

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data: Dict[str, Any] = {}
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        os.makedirs(AppConstants.DATA_DIR, exist_ok=True)
        if os.path.exists(self._settings_file):
            try:
                with open(self._settings_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data = {**self._defaults, **loaded}
            except (json.JSONDecodeError, OSError):
                self._data = dict(self._defaults)
        else:
            self._data = dict(self._defaults)

    def save(self) -> None:
        os.makedirs(AppConstants.DATA_DIR, exist_ok=True)
        try:
            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, self._defaults.get(key, default))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def reset(self) -> None:
        self._data = dict(self._defaults)
        self.save()

    def add_recent_file(self, path: str) -> None:
        recent: List[str] = self._data.get("recent_files", [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        recent = [r for r in recent if os.path.exists(r)]
        self._data["recent_files"] = recent[: AppConstants.MAX_RECENT_FILES]

    def remove_recent_file(self, path: str) -> None:
        recent: List[str] = self._data.get("recent_files", [])
        if path in recent:
            recent.remove(path)
        self._data["recent_files"] = recent

    def get_recent_files(self) -> List[str]:
        recent: List[str] = self._data.get("recent_files", [])
        return [r for r in recent if os.path.exists(r)]
