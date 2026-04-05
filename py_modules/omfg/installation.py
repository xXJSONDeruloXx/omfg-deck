"""
Installation service: downloads the omfg release zip from GitHub,
extracts layer files to the correct XDG locations and writes the initial
hot-reload config.
"""

import json
import shutil
import ssl
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from .base_service import BaseService
from .config_schema import ConfigurationManager
from .constants import (
    GITHUB_API_URL, RELEASE_ASSET_SUFFIX,
    LIB_FILENAME, JSON_FILENAME, SHADERS_DIR, WRAPPER_FILENAME,
)
from .types import InstallationResponse, UninstallationResponse, InstallationCheckResponse


def _ssl_ctx() -> ssl.SSLContext:
    """Return an SSL context suitable for Steam Deck (no cert verification)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class InstallationService(BaseService):

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def install(self) -> InstallationResponse:
        """Download latest omfg release and install layer files."""
        try:
            self._ensure_directories()

            # 1. Fetch release metadata
            asset_url, asset_name = self._get_release_asset_url()
            self.log.info(f"Downloading omfg release asset: {asset_name}")

            # 2. Download zip to a temp file
            with tempfile.TemporaryDirectory() as tmp_dir:
                zip_path = Path(tmp_dir) / asset_name
                self._download(asset_url, zip_path)

                # 3. Extract and place files
                self._extract_and_install(zip_path)

            # 4. Write default config and wrapper script
            self._write_default_config()
            self._write_wrapper_script()

            self.log.info("omfg installed successfully")
            return {"success": True, "message": "omfg installed successfully", "error": None}

        except Exception as e:
            self.log.error(f"omfg install failed: {e}")
            return {"success": False, "message": "", "error": str(e)}

    def uninstall(self) -> UninstallationResponse:
        """Remove installed omfg layer files (config is preserved)."""
        try:
            removed: list[str] = []

            for path in [self.lib_file, self.json_file]:
                if self._remove_if_exists(path):
                    removed.append(str(path))

            # Remove shaders directory
            shaders = self.lib_dir / SHADERS_DIR
            if self._remove_if_exists(shaders):
                removed.append(str(shaders))

            # Remove lib dir if now empty
            try:
                if self.lib_dir.exists() and not any(self.lib_dir.iterdir()):
                    self.lib_dir.rmdir()
                    removed.append(str(self.lib_dir))
            except OSError:
                pass

            if not removed:
                return {
                    "success": True,
                    "message": "No omfg files found to remove",
                    "removed_files": None,
                    "error": None,
                }
            return {
                "success": True,
                "message": f"omfg uninstalled. Removed {len(removed)} item(s).",
                "removed_files": removed,
                "error": None,
            }
        except Exception as e:
            return {"success": False, "message": "", "removed_files": None, "error": str(e)}

    def check_installation(self) -> InstallationCheckResponse:
        """Return installation status."""
        try:
            lib_ok = self.lib_file.exists()
            json_ok = self.json_file.exists()
            config_ok = self.config_file.exists()
            wrapper_ok = (self.config_dir / WRAPPER_FILENAME).exists()
            installed_version = ""
            if json_ok:
                try:
                    manifest = json.loads(self.json_file.read_text())
                    installed_version = manifest.get("layer", {}).get("implementation_version", "")
                except Exception:
                    pass
            return {
                "installed": lib_ok and json_ok,
                "lib_exists": lib_ok,
                "json_exists": json_ok,
                "config_exists": config_ok,
                "wrapper_exists": wrapper_ok,
                "installed_version": installed_version,
                "lib_path": str(self.lib_file),
                "json_path": str(self.json_file),
                "error": None,
            }
        except Exception as e:
            return {
                "installed": False,
                "lib_exists": False,
                "json_exists": False,
                "config_exists": False,
                "wrapper_exists": False,
                "installed_version": "",
                "lib_path": str(self.lib_file),
                "json_path": str(self.json_file),
                "error": str(e),
            }

    def cleanup_on_uninstall(self) -> None:
        """Called during plugin uninstall; removes all managed files."""
        try:
            for path in [self.lib_file, self.json_file, self.config_file,
                         self.lib_dir / SHADERS_DIR]:
                try:
                    self._remove_if_exists(path)
                except OSError:
                    pass
        except Exception as e:
            self.log.error(f"Cleanup failed: {e}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_release_asset_url(self) -> tuple[str, str]:
        """Fetch the GitHub releases API and return (download_url, filename)."""
        with urllib.request.urlopen(GITHUB_API_URL, context=_ssl_ctx()) as resp:
            data = json.loads(resp.read().decode())

        for asset in data.get("assets", []):
            name: str = asset.get("name", "")
            if name.endswith(RELEASE_ASSET_SUFFIX):
                return asset["browser_download_url"], name

        # Fallback: derive from tag
        tag = data.get("tag_name", "")
        filename = f"omfg-{tag}-linux-amd64.zip"
        url = (f"https://github.com/xXJSONDeruloXx/omfg/releases/download"
               f"/{tag}/{filename}")
        return url, filename

    def _download(self, url: str, dest: Path) -> None:
        with urllib.request.urlopen(url, context=_ssl_ctx()) as resp:
            with open(dest, "wb") as f:
                shutil.copyfileobj(resp, f)

    def _extract_and_install(self, zip_path: Path) -> None:
        """Extract layer artefacts to their target locations."""
        with zipfile.ZipFile(zip_path, "r") as zf:
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                zf.extractall(tmp_path)

                # Find the top-level directory inside the zip
                subdirs = [p for p in tmp_path.iterdir() if p.is_dir()]
                base = subdirs[0] if subdirs else tmp_path

                # .so → ~/.local/lib/omfg/
                src_so = base / LIB_FILENAME
                if src_so.exists():
                    shutil.copy2(src_so, self.lib_file)
                    self.lib_file.chmod(0o755)
                    self.log.info(f"Installed {LIB_FILENAME} → {self.lib_file}")

                # shaders/ → ~/.local/lib/omfg/shaders/
                src_shaders = base / SHADERS_DIR
                if src_shaders.exists():
                    dst_shaders = self.lib_dir / SHADERS_DIR
                    if dst_shaders.exists():
                        shutil.rmtree(dst_shaders)
                    shutil.copytree(src_shaders, dst_shaders)
                    self.log.info(f"Installed shaders → {dst_shaders}")

                # .json manifest → ~/.local/share/vulkan/implicit_layer.d/
                # Rewrite library_path to absolute so Vulkan loader can find it.
                src_json = base / JSON_FILENAME
                if src_json.exists():
                    manifest = json.loads(src_json.read_text())
                    manifest["layer"]["library_path"] = str(self.lib_file)
                    self.json_file.write_text(
                        json.dumps(manifest, indent=2) + "\n"
                    )
                    self.log.info(f"Installed {JSON_FILENAME} → {self.json_file}")

    def _write_default_config(self) -> None:
        """Write omfg-live.toml with defaults if it does not already exist."""
        if self.config_file.exists():
            self.log.info("Config file already exists; skipping default write")
            return
        toml = ConfigurationManager.generate_toml(ConfigurationManager.get_defaults())
        self._atomic_write(self.config_file, toml, 0o644)
        self.log.info(f"Wrote default config → {self.config_file}")

    def _write_wrapper_script(self) -> None:
        """Write an optional omfg-wrapper.sh the user can use as a Steam launch option."""
        wrapper_path = self.config_dir / WRAPPER_FILENAME
        config_path = str(self.config_file)
        script = f"""#!/usr/bin/env bash
# OMFG wrapper script — managed by omfg-deck Decky plugin
# Usage (Steam Launch Options):  {wrapper_path} %command%
set -euo pipefail

export ENABLE_OMFG_RUST=1
export OMFG_HOT_CONFIG_PATH="{config_path}"

# Ensure config and log dirs exist
mkdir -p "$(dirname "{config_path}")" "${{HOME}}/.local/share/omfg/logs"

exec "$@"
"""
        self._atomic_write(wrapper_path, script, 0o755)
        self.log.info(f"Wrote wrapper script → {wrapper_path}")

