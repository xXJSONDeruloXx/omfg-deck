"""
Tests for omfg.plugin — Plugin async methods and _version_newer.
"""
import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from omfg.plugin import Plugin
from omfg.config_schema import ConfigurationManager
from omfg.constants import LAYER_ENABLE_ENV, HOT_CONFIG_ENV


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(coro):
    """Run a coroutine synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)


def make_plugin(patched_home):
    """Create a Plugin with services pointing at tmp_home."""
    from omfg.installation import InstallationService
    from omfg.configuration import ConfigurationService
    from omfg.constants import LIB_DIR, VULKAN_LAYER_DIR, CONFIG_DIR, LIB_FILENAME, JSON_FILENAME, CONFIG_FILENAME

    plugin = Plugin()
    h = patched_home

    for svc in [plugin.installation_service, plugin.configuration_service]:
        svc.home = h
        svc.lib_dir = h / LIB_DIR
        svc.vulkan_layer_dir = h / VULKAN_LAYER_DIR
        svc.config_dir = h / CONFIG_DIR
        svc.lib_file = svc.lib_dir / LIB_FILENAME
        svc.json_file = svc.vulkan_layer_dir / JSON_FILENAME
        svc.config_file = svc.config_dir / CONFIG_FILENAME
        svc.log_dir = h / ".local/share/omfg/logs"

    return plugin


# ---------------------------------------------------------------------------
# check_omfg_installed
# ---------------------------------------------------------------------------

class TestCheckOmfgInstalled:
    def test_returns_not_installed_fresh(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.check_omfg_installed())
        assert result["installed"] is False
        assert result["error"] is None

    def test_returns_installed_when_files_present(self, patched_home):
        plugin = make_plugin(patched_home)
        svc = plugin.installation_service
        svc._ensure_directories()
        svc.lib_file.write_bytes(b"x")
        svc.json_file.write_text('{"layer":{"implementation_version":"1"}}')
        result = run(plugin.check_omfg_installed())
        assert result["installed"] is True
        assert result["installed_version"] == "1"


# ---------------------------------------------------------------------------
# get_omfg_config / update_omfg_config / reset_omfg_config
# ---------------------------------------------------------------------------

class TestConfigMethods:
    def test_get_config_returns_defaults_when_no_file(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.get_omfg_config())
        assert result["success"] is True
        assert result["config"] == ConfigurationManager.get_defaults()

    def test_update_config_accepts_json_string(self, patched_home):
        plugin = make_plugin(patched_home)
        cfg = ConfigurationManager.get_defaults()
        cfg["OMFG_LAYER_MODE"] = "blend"
        result = run(plugin.update_omfg_config(json.dumps(cfg)))
        assert result["success"] is True
        assert result["config"]["OMFG_LAYER_MODE"] == "blend"

    def test_update_config_returns_error_on_bad_json(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.update_omfg_config("not valid json {{{"))
        assert result["success"] is False
        assert result["error"] is not None

    def test_reset_config_restores_defaults(self, patched_home):
        plugin = make_plugin(patched_home)
        cfg = ConfigurationManager.get_defaults()
        cfg["OMFG_LAYER_MODE"] = "passthrough"
        run(plugin.update_omfg_config(json.dumps(cfg)))
        result = run(plugin.reset_omfg_config())
        assert result["success"] is True
        assert result["config"]["OMFG_LAYER_MODE"] == ConfigurationManager.get_defaults()["OMFG_LAYER_MODE"]

    def test_get_config_after_update(self, patched_home):
        plugin = make_plugin(patched_home)
        cfg = ConfigurationManager.get_defaults()
        cfg["OMFG_MULTI_BLEND_COUNT"] = 4
        run(plugin.update_omfg_config(json.dumps(cfg)))
        result = run(plugin.get_omfg_config())
        assert result["config"]["OMFG_MULTI_BLEND_COUNT"] == 4


# ---------------------------------------------------------------------------
# get_config_schema
# ---------------------------------------------------------------------------

class TestGetConfigSchema:
    def test_returns_defaults(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.get_config_schema())
        assert result["defaults"] == ConfigurationManager.get_defaults()

    def test_returns_all_modes(self, patched_home):
        from omfg.constants import ALL_LAYER_MODES
        plugin = make_plugin(patched_home)
        result = run(plugin.get_config_schema())
        assert result["modes"] == ALL_LAYER_MODES

    def test_returns_debug_views(self, patched_home):
        from omfg.constants import DEBUG_VIEWS
        plugin = make_plugin(patched_home)
        result = run(plugin.get_config_schema())
        assert result["debug_views"] == DEBUG_VIEWS


# ---------------------------------------------------------------------------
# get_launch_option
# ---------------------------------------------------------------------------

class TestGetLaunchOption:
    def test_contains_enable_env(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.get_launch_option())
        assert result["success"] is True
        assert LAYER_ENABLE_ENV + "=1" in result["launch_option"]

    def test_contains_hot_config_path(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.get_launch_option())
        assert HOT_CONFIG_ENV in result["launch_option"]
        config_path = str(plugin.configuration_service.config_file)
        assert config_path in result["launch_option"]

    def test_contains_percent_command(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.get_launch_option())
        assert "%command%" in result["launch_option"]


# ---------------------------------------------------------------------------
# uninstall_omfg
# ---------------------------------------------------------------------------

class TestUninstallOmfg:
    def test_uninstall_when_nothing_installed(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.uninstall_omfg())
        assert result["success"] is True

    def test_uninstall_removes_files(self, patched_home):
        plugin = make_plugin(patched_home)
        svc = plugin.installation_service
        svc._ensure_directories()
        svc.lib_file.write_bytes(b"x")
        svc.json_file.write_text("{}")
        result = run(plugin.uninstall_omfg())
        assert result["success"] is True
        assert not svc.lib_file.exists()


# ---------------------------------------------------------------------------
# _version_newer
# ---------------------------------------------------------------------------

class TestVersionNewer:
    @pytest.mark.parametrize("candidate,current,expected", [
        ("0.2.0", "0.1.0", True),
        ("0.1.0", "0.1.0", False),
        ("0.1.0", "0.2.0", False),
        ("1.0.0", "0.9.9", True),
        ("0.1.1", "0.1.0", True),
        ("v0.2.0", "0.1.0", True),   # v-prefix
        ("0.2.0", "v0.1.0", True),   # v-prefix on current
        ("0.10.0", "0.9.0", True),   # numeric comparison not lexicographic
        ("0.0.1", "0.0.0", True),
        ("0.0.0", "0.0.1", False),
        ("1.0", "0.9.9", True),      # different length
        ("", "0.1.0", False),        # empty string
    ])
    def test_version_comparison(self, candidate, current, expected):
        assert Plugin._version_newer(candidate, current) is expected


# ---------------------------------------------------------------------------
# check_for_plugin_update — network mocked
# ---------------------------------------------------------------------------

class TestCheckForPluginUpdate:
    def _mock_api_response(self, tag="v0.2.0", asset_name="omfg-deck.zip"):
        body = json.dumps({
            "tag_name": tag,
            "body": "release notes",
            "published_at": "2026-04-05T00:00:00Z",
            "assets": [{"name": asset_name, "browser_download_url": f"http://example.com/{asset_name}"}],
        }).encode()
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = body
        return mock_resp

    def test_detects_update_available(self, patched_home, mock_decky):
        mock_decky.DECKY_PLUGIN_DIR = str(patched_home)
        pkg = patched_home / "package.json"
        pkg.write_text(json.dumps({"version": "0.1.0"}))
        plugin = make_plugin(patched_home)

        with patch("urllib.request.urlopen", return_value=self._mock_api_response("v0.2.0")):
            result = run(plugin.check_for_plugin_update())

        assert result["success"] is True
        assert result["update_available"] is True
        assert result["latest_version"] == "0.2.0"
        assert result["current_version"] == "0.1.0"

    def test_no_update_when_on_latest(self, patched_home, mock_decky):
        mock_decky.DECKY_PLUGIN_DIR = str(patched_home)
        pkg = patched_home / "package.json"
        pkg.write_text(json.dumps({"version": "0.2.0"}))
        plugin = make_plugin(patched_home)

        with patch("urllib.request.urlopen", return_value=self._mock_api_response("v0.2.0")):
            result = run(plugin.check_for_plugin_update())

        assert result["success"] is True
        assert result["update_available"] is False

    def test_returns_download_url(self, patched_home, mock_decky):
        mock_decky.DECKY_PLUGIN_DIR = str(patched_home)
        (patched_home / "package.json").write_text(json.dumps({"version": "0.1.0"}))
        plugin = make_plugin(patched_home)

        with patch("urllib.request.urlopen", return_value=self._mock_api_response()):
            result = run(plugin.check_for_plugin_update())

        assert result["download_url"].endswith(".zip")

    def test_handles_network_error(self, patched_home, mock_decky):
        mock_decky.DECKY_PLUGIN_DIR = str(patched_home)
        (patched_home / "package.json").write_text(json.dumps({"version": "0.1.0"}))
        plugin = make_plugin(patched_home)

        with patch("urllib.request.urlopen", side_effect=OSError("network down")):
            result = run(plugin.check_for_plugin_update())

        assert result["success"] is False
        assert "error" in result

    def test_uses_default_version_when_package_json_missing(self, patched_home, mock_decky):
        mock_decky.DECKY_PLUGIN_DIR = str(patched_home)
        plugin = make_plugin(patched_home)

        with patch("urllib.request.urlopen", return_value=self._mock_api_response("v0.2.0")):
            result = run(plugin.check_for_plugin_update())

        assert result["current_version"] == "0.0.0"
        assert result["update_available"] is True


# ---------------------------------------------------------------------------
# download_plugin_update — network mocked
# ---------------------------------------------------------------------------

class TestDownloadPluginUpdate:
    def test_downloads_to_downloads_dir(self, patched_home, mock_decky):
        downloads = patched_home / "Downloads"
        plugin = make_plugin(patched_home)

        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = b"fake zip content"

        with patch("urllib.request.urlopen", return_value=mock_resp), \
             patch.object(Path, "home", return_value=patched_home):
            result = run(plugin.download_plugin_update("http://example.com/omfg-deck.zip"))

        assert result["success"] is True
        assert result["download_path"].endswith("omfg-deck.zip")

    def test_returns_error_on_network_failure(self, patched_home, mock_decky):
        plugin = make_plugin(patched_home)
        with patch("urllib.request.urlopen", side_effect=OSError("timeout")):
            result = run(plugin.download_plugin_update("http://example.com/x.zip"))
        assert result["success"] is False
        assert result["error"] is not None


# ---------------------------------------------------------------------------
# get_layer_enabled / set_layer_enabled
# ---------------------------------------------------------------------------

class TestLayerEnabledMethods:
    def test_enabled_by_default_when_no_env_file(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.get_layer_enabled())
        assert result["success"] is True
        assert result["enabled"] is True

    def test_set_disabled_then_read_back(self, patched_home, mock_decky):
        plugin = make_plugin(patched_home)
        run(plugin.set_layer_enabled(False))
        result = run(plugin.get_layer_enabled())
        assert result["success"] is True
        assert result["enabled"] is False

    def test_set_enabled_then_read_back(self, patched_home, mock_decky):
        plugin = make_plugin(patched_home)
        run(plugin.set_layer_enabled(False))
        run(plugin.set_layer_enabled(True))
        result = run(plugin.get_layer_enabled())
        assert result["enabled"] is True

    def test_env_file_created(self, patched_home, mock_decky):
        plugin = make_plugin(patched_home)
        run(plugin.set_layer_enabled(False))
        env_path = plugin.configuration_service.config_dir / "omfg.env"
        assert env_path.exists()
        assert "OMFG_DISABLE_LAYER=1" in env_path.read_text()


# ---------------------------------------------------------------------------
# get_layer_log
# ---------------------------------------------------------------------------

class TestGetLayerLog:
    def test_returns_empty_when_no_log(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.get_layer_log(50))
        assert result["success"] is True
        assert result["log"] == ""

    def test_returns_last_n_lines(self, patched_home):
        plugin = make_plugin(patched_home)
        log_dir = plugin.installation_service.log_dir
        log_dir.mkdir(parents=True, exist_ok=True)
        lines = [f"line {i}" for i in range(100)]
        (log_dir / "omfg.log").write_text("\n".join(lines))

        result = run(plugin.get_layer_log(10))
        assert result["success"] is True
        returned = result["log"].splitlines()
        assert len(returned) == 10
        assert returned[-1] == "line 99"


# ---------------------------------------------------------------------------
# Edge-case branches for layer-enabled and log methods
# ---------------------------------------------------------------------------

class TestLayerEnabledEdgeCases:
    def test_env_file_with_no_disable_key_returns_enabled(self, patched_home, mock_decky):
        """File exists but has no OMFG_DISABLE_LAYER line → enabled=True fallback."""
        plugin = make_plugin(patched_home)
        plugin.configuration_service.config_dir.mkdir(parents=True, exist_ok=True)
        env = plugin.configuration_service.config_dir / "omfg.env"
        env.write_text("# comment only\nSOME_OTHER_VAR=1\n")
        result = run(plugin.get_layer_enabled())
        assert result["success"] is True
        assert result["enabled"] is True

    def test_get_layer_enabled_exception_returns_error(self, patched_home, monkeypatch):
        plugin = make_plugin(patched_home)
        monkeypatch.setattr(
            plugin.configuration_service.config_dir.__class__, "exists",
            lambda s: (_ for _ in ()).throw(RuntimeError("stat error"))
        )
        # Make the config_dir.exists() raise
        from unittest.mock import patch as _patch
        with _patch.object(Path, "exists", side_effect=RuntimeError("stat error")):
            result = run(plugin.get_layer_enabled())
        assert result["success"] is False
        assert result["enabled"] is True   # safe default

    def test_set_layer_enabled_exception_returns_error(self, patched_home, mock_decky):
        plugin = make_plugin(patched_home)
        from unittest.mock import patch as _patch
        with _patch.object(
            plugin.configuration_service, "_atomic_write",
            side_effect=OSError("disk full")
        ):
            result = run(plugin.set_layer_enabled(False))
        assert result["success"] is False
        assert result["error"] is not None

    def test_get_layer_log_exception_returns_error(self, patched_home):
        plugin = make_plugin(patched_home)
        log_dir = plugin.installation_service.log_dir
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "omfg.log"
        log_file.write_text("some log")
        from unittest.mock import patch as _patch
        with _patch.object(Path, "read_text", side_effect=OSError("perm denied")):
            result = run(plugin.get_layer_log(10))
        assert result["success"] is False
        assert result["error"] is not None


# ---------------------------------------------------------------------------
# Workaround methods
# ---------------------------------------------------------------------------

class TestWorkarounds:
    def test_defaults_off(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.get_workarounds())
        assert result["success"] is True
        assert result["mesa_immediate"] is False
        assert result["disable_vkbasalt"] is False

    def test_set_mesa_immediate_on(self, patched_home):
        plugin = make_plugin(patched_home)
        run(plugin.set_workaround("mesa_immediate", True))
        result = run(plugin.get_workarounds())
        assert result["mesa_immediate"] is True
        assert result["disable_vkbasalt"] is False   # other unchanged

    def test_set_disable_vkbasalt_on(self, patched_home):
        plugin = make_plugin(patched_home)
        run(plugin.set_workaround("disable_vkbasalt", True))
        result = run(plugin.get_workarounds())
        assert result["disable_vkbasalt"] is True

    def test_disable_layer_persists_after_workaround_write(self, patched_home, mock_decky):
        """Setting a workaround must not clobber the layer-enabled flag."""
        plugin = make_plugin(patched_home)
        run(plugin.set_layer_enabled(False))
        run(plugin.set_workaround("mesa_immediate", True))
        assert run(plugin.get_layer_enabled())["enabled"] is False
        assert run(plugin.get_workarounds())["mesa_immediate"] is True

    def test_invalid_key_returns_error(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.set_workaround("nonexistent_key", True))
        assert result["success"] is False

    def test_get_launch_option_includes_mesa_when_enabled(self, patched_home):
        plugin = make_plugin(patched_home)
        run(plugin.set_workaround("mesa_immediate", True))
        result = run(plugin.get_launch_option())
        assert "MESA_VK_WSI_PRESENT_MODE=immediate" in result["launch_option"]

    def test_get_launch_option_includes_vkbasalt_when_enabled(self, patched_home):
        plugin = make_plugin(patched_home)
        run(plugin.set_workaround("disable_vkbasalt", True))
        result = run(plugin.get_launch_option())
        assert "DISABLE_VKBASALT=1" in result["launch_option"]

    def test_get_launch_option_no_workarounds_by_default(self, patched_home):
        plugin = make_plugin(patched_home)
        result = run(plugin.get_launch_option())
        assert "MESA" not in result["launch_option"]
        assert "VKBASALT" not in result["launch_option"]
        assert "ENABLE_OMFG_RUST=1" in result["launch_option"]

    def test_get_launch_option_ordering(self, patched_home):
        """Workarounds should appear before ENABLE_OMFG_RUST."""
        plugin = make_plugin(patched_home)
        run(plugin.set_workaround("mesa_immediate", True))
        run(plugin.set_workaround("disable_vkbasalt", True))
        opt = run(plugin.get_launch_option())["launch_option"]
        mesa_pos = opt.index("MESA")
        omfg_pos = opt.index("ENABLE_OMFG_RUST")
        assert mesa_pos < omfg_pos


class TestWorkaroundsExceptions:
    def test_get_workarounds_exception_returns_error(self, patched_home, monkeypatch):
        plugin = make_plugin(patched_home)
        with patch.object(plugin, "_read_env", side_effect=RuntimeError("io error")):
            result = run(plugin.get_workarounds())
        assert result["success"] is False
        assert result["mesa_immediate"] is False

    def test_set_workaround_write_failure_returns_error(self, patched_home, monkeypatch):
        plugin = make_plugin(patched_home)
        with patch.object(plugin, "_set_env_flag", side_effect=OSError("disk full")):
            result = run(plugin.set_workaround("mesa_immediate", True))
        assert result["success"] is False
        assert result["error"] is not None
