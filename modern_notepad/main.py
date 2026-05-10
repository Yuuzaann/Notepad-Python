#!/usr/bin/env python3
"""
Modern Notepad Pro — Entry Point
"""
import sys
import os

# Ensure current directory is in the path for clean imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QIcon, QFont

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
