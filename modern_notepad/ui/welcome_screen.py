from __future__ import annotations
from typing import Optional, List, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QFont, QColor
from core.constants import AppConstants


class WelcomeActionCard(QFrame):
    clicked = Signal()

    def __init__(self, icon: str, title: str, subtitle: str, parent=None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(160, 100)
        self.setObjectName("welcomeCard")
        self.setStyleSheet("""
            #welcomeCard {
                border-radius: 8px;
                border: 1px solid #2d2d2d;
            }
            #welcomeCard:hover {
                border-color: #007acc;
                background: #1e2530;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 20))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 11)
        title_font.setWeight(QFont.Weight.Medium)
        title_label.setFont(title_font)

        sub_label = QLabel(subtitle)
        sub_font = QFont("Segoe UI", 9)
        sub_label.setFont(sub_font)
        sub_label.setObjectName("subtitle")

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(sub_label)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class WelcomeScreen(QWidget):
    new_file_requested = Signal()
    open_file_requested = Signal()
    open_folder_requested = Signal()
    recent_file_requested = Signal(str)

    def __init__(self, recent_files: List[str] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._recent_files = recent_files or []
        self._build_ui()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(40)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        logo_label = QLabel("📝")
        logo_label.setFont(QFont("Segoe UI", 48))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(AppConstants.APP_NAME)
        title_font = QFont("Segoe UI", 28)
        title_font.setWeight(QFont.Weight.Light)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("title")

        version_label = QLabel(f"v{AppConstants.APP_VERSION}  •  Professional Code Editor")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setObjectName("subtitle")

        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addWidget(version_label)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(16)
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        new_card = WelcomeActionCard("✦", "New File", "Ctrl+N")
        new_card.clicked.connect(self.new_file_requested.emit)

        open_card = WelcomeActionCard("📂", "Open File", "Ctrl+O")
        open_card.clicked.connect(self.open_file_requested.emit)

        folder_card = WelcomeActionCard("🗂", "Open Folder", "Ctrl+Shift+O")
        folder_card.clicked.connect(self.open_folder_requested.emit)

        actions_layout.addWidget(new_card)
        actions_layout.addWidget(open_card)
        actions_layout.addWidget(folder_card)

        main_layout.addLayout(header_layout)
        main_layout.addLayout(actions_layout)

        if self._recent_files:
            recent_section = self._build_recent_section()
            main_layout.addWidget(recent_section)

        main_layout.addStretch()

    def _build_recent_section(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        section_label = QLabel("Recent Files")
        section_font = QFont("Segoe UI", 12)
        section_font.setWeight(QFont.Weight.Medium)
        section_label.setFont(section_font)

        layout.addWidget(section_label)

        for path in self._recent_files[:8]:
            import os
            btn = QPushButton(f"  {os.path.basename(path)}  —  {os.path.dirname(path)}")
            btn.setObjectName("secondary")
            btn.setFixedHeight(32)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    background: transparent;
                    border: none;
                    color: #cccccc;
                    font-size: 12px;
                    border-radius: 4px;
                    padding: 0 8px;
                }
                QPushButton:hover {
                    background: #2a2d2e;
                    color: #ffffff;
                }
            """)
            btn.clicked.connect(lambda checked, p=path: self.recent_file_requested.emit(p))
            layout.addWidget(btn)

        return container
