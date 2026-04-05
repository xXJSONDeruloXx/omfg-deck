"""
Configuration service: reads / writes omfg-live.toml.
"""

import json
from typing import Dict, Any

from .base_service import BaseService
from .config_schema import ConfigurationManager, OmfgConfig
from .types import ConfigurationResponse


class ConfigurationService(BaseService):

    def get_config(self) -> ConfigurationResponse:
        try:
            if not self.config_file.exists():
                return {
                    "success": True,
                    "config": ConfigurationManager.get_defaults(),
                    "message": "Config file not found; returning defaults",
                    "error": None,
                }
            content = self.config_file.read_text(encoding="utf-8")
            config = ConfigurationManager.parse_toml(content)
            return {"success": True, "config": config, "message": None, "error": None}
        except Exception as e:
            self.log.error(f"Error reading config: {e}")
            return {
                "success": False,
                "config": None,
                "message": None,
                "error": str(e),
            }

    def update_config(self, config_dict: Dict[str, Any]) -> ConfigurationResponse:
        try:
            validated = ConfigurationManager.validate(config_dict)
            toml = ConfigurationManager.generate_toml(validated)
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self._atomic_write(self.config_file, toml, 0o644)
            self.log.info("omfg config updated")
            return {"success": True, "config": validated, "message": "Config updated", "error": None}
        except Exception as e:
            self.log.error(f"Error updating config: {e}")
            return {"success": False, "config": None, "message": None, "error": str(e)}

    def update_field(self, key: str, value: Any) -> ConfigurationResponse:
        """Convenience: update a single field by env-var name."""
        current_resp = self.get_config()
        config: dict = dict(current_resp.get("config") or ConfigurationManager.get_defaults())
        config[key] = value
        return self.update_config(config)
