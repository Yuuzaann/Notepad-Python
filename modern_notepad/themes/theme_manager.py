import os
from typing import Dict, Optional
from PySide6.QtWidgets import QApplication
from utils.logger import get_logger

logger = get_logger("ThemeManager")

THEMES_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_qss(theme_name: str) -> str:
    path = os.path.join(THEMES_DIR, f"{theme_name.lower()}_theme.qss")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    logger.warning("Theme file not found: %s", path)
    return ""


AVAILABLE_THEMES = ["Dark", "Light", "Dracula", "Midnight"]


class ThemeManager:
    _instance: Optional["ThemeManager"] = None

    def __new__(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current_theme = "Dark"
            cls._instance._cache: Dict[str, str] = {}
        return cls._instance

    def apply_theme(self, theme_name: str, app: Optional[QApplication] = None) -> None:
        if theme_name not in AVAILABLE_THEMES:
            logger.warning("Unknown theme: %s, using Dark", theme_name)
            theme_name = "Dark"

        if theme_name not in self._cache:
            self._cache[theme_name] = _load_qss(theme_name)

        qss = self._cache[theme_name]
        target = app or QApplication.instance()
        if target:
            target.setStyleSheet(qss)
        self._current_theme = theme_name
        logger.info("Applied theme: %s", theme_name)

    @property
    def current_theme(self) -> str:
        return self._current_theme

    @property
    def available_themes(self):
        return AVAILABLE_THEMES

    def is_dark(self) -> bool:
        return self._current_theme.lower() in ("dark", "dracula", "midnight")
