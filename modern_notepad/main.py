#!/usr/bin/env python3
"""
Modern Notepad Pro — Entry Point
"""
import sys
import os

# Ensure the app directory is on the path for clean imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _check_dependencies() -> None:
    missing = []
    try:
        import PySide6
    except ImportError:
        missing.append("PySide6")
    try:
        import pygments
    except ImportError:
        missing.append("Pygments")

    if missing:
        pkgs = " ".join(missing)
        print(
            f"\n[Modern Notepad Pro] Missing dependencies: {', '.join(missing)}\n"
            f"Install them with:\n\n    pip install {pkgs}\n"
        )
        if "PySide6" in missing:
            sys.exit(1)


_check_dependencies()

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QFont

from core.constants import AppConstants
from utils.logger import get_logger

logger = get_logger("Main")


def setup_app() -> QApplication:
    QCoreApplication.setApplicationName(AppConstants.APP_NAME)
    QCoreApplication.setApplicationVersion(AppConstants.APP_VERSION)
    QCoreApplication.setOrganizationName(AppConstants.APP_AUTHOR)

    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    return app


def main() -> int:
    logger.info("Starting %s v%s", AppConstants.APP_NAME, AppConstants.APP_VERSION)

    app = setup_app()

    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    logger.info("Application started")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
