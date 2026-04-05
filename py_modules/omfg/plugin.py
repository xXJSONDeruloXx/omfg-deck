"""
Main Plugin class for the omfg-deck Decky Loader plugin.
"""

import json
import os
import ssl
import urllib.request
from pathlib import Path
from typing import Dict, Any

from .installation import InstallationService
from .configuration import ConfigurationService
from .config_schema import ConfigurationManager
from .constants import (
    ALL_LAYER_MODES, DEBUG_VIEWS,
    LAYER_ENABLE_ENV, HOT_CONFIG_ENV,
)


class Plugin:

    def __init__(self):
        self.installation_service = InstallationService()
        self.configuration_service = ConfigurationService()

    # ------------------------------------------------------------------
    # Installation
    # ------------------------------------------------------------------

    async def install_omfg(self) -> Dict[str, Any]:
        return self.installation_service.install()

    async def uninstall_omfg(self) -> Dict[str, Any]:
        return self.installation_service.uninstall()

    async def check_omfg_installed(self) -> Dict[str, Any]:
        return self.installation_service.check_installation()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    async def get_omfg_config(self) -> Dict[str, Any]:
        return self.configuration_service.get_config()

    async def update_omfg_config(self, config_json: str) -> Dict[str, Any]:
        """Receive config as a JSON string from the frontend."""
        try:
            config_dict = json.loads(config_json)
            return self.configuration_service.update_config(config_dict)
        except Exception as e:
            return {"success": False, "config": None, "message": None, "error": str(e)}

    async def get_config_schema(self) -> Dict[str, Any]:
        """Return schema metadata for the frontend."""
        return {
            "defaults": ConfigurationManager.get_defaults(),
            "modes": ALL_LAYER_MODES,
            "debug_views": DEBUG_VIEWS,
        }

    async def reset_omfg_config(self) -> Dict[str, Any]:
        """Reset omfg-live.toml to factory defaults."""
        return self.configuration_service.reset_config()

    async def get_launch_option(self) -> Dict[str, Any]:
        """Return the Steam launch option string for per-game activation."""
        config_path = str(self.configuration_service.config_file)
        launch_opt = (
            f"{LAYER_ENABLE_ENV}=1 "
            f"{HOT_CONFIG_ENV}={config_path} "
            "%command%"
        )
        return {"success": True, "launch_option": launch_opt}

    # ------------------------------------------------------------------
    # Self-updater
    # ------------------------------------------------------------------

    async def check_for_plugin_update(self) -> Dict[str, Any]:
        try:
            import decky
            pkg_path = Path(decky.DECKY_PLUGIN_DIR) / "package.json"
            current = "0.0.0"
            if pkg_path.exists():
                current = json.loads(pkg_path.read_text()).get("version", "0.0.0")

            api_url = ("https://api.github.com/repos/"
                       "xXJSONDeruloXx/omfg-deck/releases/latest")
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(api_url, context=ctx) as resp:
                data = json.loads(resp.read())

            latest = data.get("tag_name", "").lstrip("v")
            notes = data.get("body", "")
            date = data.get("published_at", "")
            dl_url = ""
            for asset in data.get("assets", []):
                if asset.get("name", "").endswith(".zip"):
                    dl_url = asset["browser_download_url"]
                    break

            return {
                "success": True,
                "update_available": self._version_newer(latest, current),
                "current_version": current,
                "latest_version": latest,
                "release_notes": notes,
                "release_date": date,
                "download_url": dl_url,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def download_plugin_update(self, download_url: str) -> Dict[str, Any]:
        try:
            dst = Path.home() / "Downloads" / "omfg-deck.zip"
            dst.parent.mkdir(exist_ok=True)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(download_url, context=ctx) as resp:
                dst.write_bytes(resp.read())
            if dst.exists() and dst.stat().st_size > 0:
                return {"success": True, "download_path": str(dst)}
            return {"success": False, "error": "Downloaded file is empty"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def _main(self):
        import decky
        decky.logger.info("omfg-deck plugin loaded")

    async def _unload(self):
        import decky
        decky.logger.info("omfg-deck plugin unloading")

    async def _uninstall(self):
        import decky
        decky.logger.info("omfg-deck plugin uninstall – running cleanup")
        self.installation_service.cleanup_on_uninstall()

    async def _migration(self):
        import decky
        decky.logger.info("omfg-deck: running migrations")
        decky.migrate_logs(
            os.path.join(decky.DECKY_USER_HOME, ".config", "omfg-deck", "omfg-deck.log")
        )
        decky.migrate_settings(
            os.path.join(decky.DECKY_HOME, "settings", "omfg-deck.json"),
            os.path.join(decky.DECKY_USER_HOME, ".config", "omfg-deck"),
        )
        decky.migrate_runtime(
            os.path.join(decky.DECKY_HOME, "omfg-deck"),
            os.path.join(decky.DECKY_USER_HOME, ".local", "share", "omfg-deck"),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _version_newer(candidate: str, current: str) -> bool:
        def parts(v: str):
            try:
                return [int(x) for x in v.lstrip("v").split(".")]
            except ValueError:
                return [0]
        c, r = parts(candidate), parts(current)
        length = max(len(c), len(r))
        c += [0] * (length - len(c))
        r += [0] * (length - len(r))
        return c > r
