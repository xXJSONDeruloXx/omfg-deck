"""
Base service class with common path helpers.
"""

import tempfile
from pathlib import Path
from typing import Any, Optional

from .constants import LIB_DIR, VULKAN_LAYER_DIR, CONFIG_DIR, LOG_DIR, LIB_FILENAME, JSON_FILENAME, CONFIG_FILENAME


class BaseService:
    """Base service with shared paths and helpers."""

    def __init__(self, logger: Optional[Any] = None):
        if logger is None:
            import decky
            self.log = decky.logger
        else:
            self.log = logger

        self.home = Path.home()
        self.lib_dir = self.home / LIB_DIR
        self.vulkan_layer_dir = self.home / VULKAN_LAYER_DIR
        self.config_dir = self.home / CONFIG_DIR
        self.log_dir = self.home / LOG_DIR

        self.lib_file = self.lib_dir / LIB_FILENAME
        self.json_file = self.vulkan_layer_dir / JSON_FILENAME
        self.config_file = self.config_dir / CONFIG_FILENAME

    def _ensure_directories(self) -> None:
        self.lib_dir.mkdir(parents=True, exist_ok=True)
        self.vulkan_layer_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _remove_if_exists(self, path: Path) -> bool:
        if path.exists():
            try:
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
                self.log.info(f"Removed {path}")
                return True
            except OSError as e:
                self.log.error(f"Failed to remove {path}: {e}")
                raise
        return False

    def _atomic_write(self, path: Path, content: str, mode: int = 0o644) -> None:
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=path.parent,
                delete=False,
                prefix=f'.{path.name}.',
                suffix='.tmp'
            ) as tmp:
                tmp.write(content)
                temp_path = Path(tmp.name)
            temp_path.chmod(mode)
            temp_path.replace(path)
        except Exception:
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise
