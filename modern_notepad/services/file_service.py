import os
import shutil
from datetime import datetime
from typing import Optional, Tuple
from models.file_model import FileModel
from core.constants import AppConstants
from utils.logger import get_logger

logger = get_logger("FileService")


class FileService:
    def __init__(self) -> None:
        os.makedirs(AppConstants.TEMP_DIR, exist_ok=True)
        os.makedirs(AppConstants.BACKUP_DIR, exist_ok=True)

    def read_file(self, path: str) -> Tuple[str, str]:
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"]
        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as f:
                    content = f.read()
                logger.info("Opened file: %s (encoding: %s)", path, encoding)
                return content, encoding.upper().replace("-SIG", "")
            except (UnicodeDecodeError, LookupError):
                continue
            except OSError as e:
                logger.error("Failed to read %s: %s", path, e)
                raise
        raise UnicodeDecodeError("utf-8", b"", 0, 1, f"Cannot decode file: {path}")

    def write_file(self, path: str, content: str, encoding: str = "UTF-8") -> bool:
        try:
            normalized = encoding.upper().replace("-SIG", "")
            codec = "utf-8" if normalized in ("UTF-8", "UTF8") else encoding.lower()
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
            with open(path, "w", encoding=codec, newline="") as f:
                f.write(content)
            logger.info("Saved file: %s", path)
            return True
        except OSError as e:
            logger.error("Failed to write %s: %s", path, e)
            return False

    def create_backup(self, path: str, content: str) -> Optional[str]:
        try:
            filename = os.path.basename(path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{filename}.{timestamp}.bak"
            backup_path = os.path.join(AppConstants.BACKUP_DIR, backup_name)
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)
            self._cleanup_old_backups(filename)
            return backup_path
        except OSError as e:
            logger.warning("Backup failed for %s: %s", path, e)
            return None

    def _cleanup_old_backups(self, filename: str, keep: int = 5) -> None:
        try:
            backups = sorted(
                [
                    f for f in os.listdir(AppConstants.BACKUP_DIR)
                    if f.startswith(filename) and f.endswith(".bak")
                ]
            )
            for old in backups[:-keep]:
                os.remove(os.path.join(AppConstants.BACKUP_DIR, old))
        except OSError:
            pass

    def save_temp(self, tab_id: int, content: str) -> str:
        temp_path = os.path.join(AppConstants.TEMP_DIR, f"tab_{tab_id}.tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError:
            pass
        return temp_path

    def read_temp(self, tab_id: int) -> Optional[str]:
        temp_path = os.path.join(AppConstants.TEMP_DIR, f"tab_{tab_id}.tmp")
        if os.path.exists(temp_path):
            try:
                with open(temp_path, "r", encoding="utf-8") as f:
                    return f.read()
            except OSError:
                pass
        return None

    def delete_temp(self, tab_id: int) -> None:
        temp_path = os.path.join(AppConstants.TEMP_DIR, f"tab_{tab_id}.tmp")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

    def get_file_info(self, path: str) -> dict:
        if not os.path.exists(path):
            return {}
        stat = os.stat(path)
        return {
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        }
