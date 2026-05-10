from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TabModel:
    id: int = 0
    file_path: Optional[str] = None
    title: str = "Untitled"
    content: str = ""
    cursor_position: int = 0
    scroll_position: int = 0
    is_modified: bool = False
    encoding: str = "UTF-8"
    tab_order: int = 0

    @property
    def display_title(self) -> str:
        prefix = "* " if self.is_modified else ""
        return f"{prefix}{self.title}"

    @property
    def is_saved(self) -> bool:
        return self.file_path is not None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "file_path": self.file_path,
            "title": self.title,
            "content": self.content,
            "cursor_position": self.cursor_position,
            "scroll_position": self.scroll_position,
            "is_modified": self.is_modified,
            "encoding": self.encoding,
            "tab_order": self.tab_order,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TabModel:
        return cls(
            id=data.get("id", 0),
            file_path=data.get("file_path"),
            title=data.get("title", "Untitled"),
            content=data.get("content", ""),
            cursor_position=data.get("cursor_position", 0),
            scroll_position=data.get("scroll_position", 0),
            is_modified=bool(data.get("is_modified", False)),
            encoding=data.get("encoding", "UTF-8"),
            tab_order=data.get("tab_order", 0),
        )
