from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
from core.constants import SUPPORTED_EXTENSIONS


@dataclass
class FileModel:
    path: str
    content: str = ""
    encoding: str = "UTF-8"
    line_ending: str = "\n"
    last_modified: float = 0.0

    @property
    def filename(self) -> str:
        return os.path.basename(self.path)

    @property
    def extension(self) -> str:
        _, ext = os.path.splitext(self.path)
        return ext.lower()

    @property
    def language(self) -> str:
        return SUPPORTED_EXTENSIONS.get(self.extension, "Plain Text")

    @property
    def directory(self) -> str:
        return os.path.dirname(self.path)

    @property
    def exists(self) -> bool:
        return os.path.isfile(self.path)

    @property
    def size(self) -> int:
        if self.exists:
            return os.path.getsize(self.path)
        return 0

    def refresh_modified_time(self) -> None:
        if self.exists:
            self.last_modified = os.path.getmtime(self.path)

    def has_external_changes(self) -> bool:
        if not self.exists:
            return False
        current_mtime = os.path.getmtime(self.path)
        return current_mtime != self.last_modified
