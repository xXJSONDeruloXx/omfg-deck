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
    ENV_FILENAME, LOG_FILENAME,
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
        """Return the Steam launch option string, including active workarounds."""
        config_path = str(self.configuration_service.config_file)
        flags = self._read_env()

        # Build prefix from active workarounds
        prefix_parts = []
        if flags.get("WORKAROUND_MESA_IMMEDIATE", "0") == "1":
            prefix_parts.append("MESA_VK_WSI_PRESENT_MODE=immediate")
        if flags.get("WORKAROUND_DISABLE_VKBASALT", "0") == "1":
            prefix_parts.append("DISABLE_VKBASALT=1")

        prefix_parts += [
            f"{LAYER_ENABLE_ENV}=1",
            f"{HOT_CONFIG_ENV}={config_path}",
        ]
        launch_opt = " ".join(prefix_parts) + " %command%"
        return {"success": True, "launch_option": launch_opt}

    # ------------------------------------------------------------------
    # omfg.env: shared key/value store for plugin-managed flags
    # ------------------------------------------------------------------

    def _env_path(self) -> Path:
        return self.configuration_service.config_dir / ENV_FILENAME

    def _read_env(self) -> Dict[str, str]:
        """Read all key=value pairs from omfg.env (ignores comments)."""
        flags: Dict[str, str] = {}
        p = self._env_path()
        if not p.exists():
            return flags
        for raw in p.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            flags[key.strip()] = val.strip()
        return flags

    def _write_env(self, flags: Dict[str, str]) -> None:
        """Write key=value pairs to omfg.env atomically."""
        config_dir = self.configuration_service.config_dir
        config_dir.mkdir(parents=True, exist_ok=True)
        lines = ["# omfg-deck managed flags — do not edit by hand"]
        for key, val in sorted(flags.items()):
            lines.append(f"{key}={val}")
        lines.append("")
        self.configuration_service._atomic_write(
            self._env_path(), "\n".join(lines), 0o644
        )

    def _set_env_flag(self, key: str, value: str) -> None:
        flags = self._read_env()
        flags[key] = value
        self._write_env(flags)

    # ------------------------------------------------------------------
    # Layer enable / log
    # ------------------------------------------------------------------

    async def get_layer_enabled(self) -> Dict[str, Any]:
        """Read the global layer-enabled flag from omfg.env."""
        try:
            flags = self._read_env()
            enabled = flags.get("OMFG_DISABLE_LAYER", "0") != "1"
            return {"success": True, "enabled": enabled}
        except Exception as e:
            return {"success": False, "enabled": True, "error": str(e)}

    async def set_layer_enabled(self, enabled: bool) -> Dict[str, Any]:
        """Write OMFG_DISABLE_LAYER to omfg.env to globally enable/disable."""
        try:
            self._set_env_flag("OMFG_DISABLE_LAYER", "0" if enabled else "1")
            import decky
            decky.logger.info(f"Layer globally {'enabled' if enabled else 'disabled'}")
            return {"success": True, "enabled": enabled}
        except Exception as e:
            return {"success": False, "enabled": True, "error": str(e)}

    # ------------------------------------------------------------------
    # Workarounds
    # ------------------------------------------------------------------

    async def get_workarounds(self) -> Dict[str, Any]:
        """Return the current state of all workaround flags."""
        try:
            flags = self._read_env()
            return {
                "success": True,
                "mesa_immediate": flags.get("WORKAROUND_MESA_IMMEDIATE", "0") == "1",
                "disable_vkbasalt": flags.get("WORKAROUND_DISABLE_VKBASALT", "0") == "1",
            }
        except Exception as e:
            return {"success": False, "mesa_immediate": False, "disable_vkbasalt": False, "error": str(e)}

    async def set_workaround(self, key: str, enabled: bool) -> Dict[str, Any]:
        """Toggle a single workaround flag. key: 'mesa_immediate' | 'disable_vkbasalt'."""
        KEY_MAP = {
            "mesa_immediate": "WORKAROUND_MESA_IMMEDIATE",
            "disable_vkbasalt": "WORKAROUND_DISABLE_VKBASALT",
        }
        if key not in KEY_MAP:
            return {"success": False, "error": f"Unknown workaround key: {key}"}
        try:
            self._set_env_flag(KEY_MAP[key], "1" if enabled else "0")
            return {"success": True, "key": key, "enabled": enabled}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_layer_log(self, lines: int = 50) -> Dict[str, Any]:
        """Return the last N lines of the OMFG layer log file."""
        try:
            log_path = self.installation_service.log_dir / LOG_FILENAME
            if not log_path.exists():
                return {"success": True, "log": "", "message": "Log file not found"}
            text = log_path.read_text(errors="replace")
            tail = "\n".join(text.splitlines()[-lines:])
            return {"success": True, "log": tail, "message": None}
        except Exception as e:
            return {"success": False, "log": "", "error": str(e)}

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
