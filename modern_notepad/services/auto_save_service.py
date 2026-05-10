from typing import Callable, Optional
from PySide6.QtCore import QTimer
from core.constants import AppConstants
from utils.logger import get_logger

logger = get_logger("AutoSaveService")


class AutoSaveService:
    def __init__(self, on_save: Callable[[], None]) -> None:
        self._on_save = on_save
        self._timer = QTimer()
        self._timer.timeout.connect(self._trigger_save)
        self._enabled = False

    def start(self, interval_ms: int = AppConstants.AUTO_SAVE_INTERVAL) -> None:
        self._enabled = True
        self._timer.start(interval_ms)
        logger.debug("AutoSave started with interval %dms", interval_ms)

    def stop(self) -> None:
        self._enabled = False
        self._timer.stop()
        logger.debug("AutoSave stopped")

    def set_interval(self, interval_ms: int) -> None:
        was_active = self._timer.isActive()
        self._timer.stop()
        if was_active and self._enabled:
            self._timer.start(interval_ms)

    def _trigger_save(self) -> None:
        if self._enabled:
            logger.debug("AutoSave triggered")
            try:
                self._on_save()
            except Exception as e:
                logger.error("AutoSave error: %s", e)

    @property
    def is_running(self) -> bool:
        return self._timer.isActive()
