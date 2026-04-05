"""
Coverage gap tests: lifecycle methods, atomic_write/remove failure paths,
full install() orchestration, config_schema parse branch.
"""
import asyncio
import json
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest

from omfg.plugin import Plugin
from omfg.base_service import BaseService
from omfg.config_schema import ConfigurationManager
from omfg.constants import (
    LIB_DIR, VULKAN_LAYER_DIR, CONFIG_DIR,
    LIB_FILENAME, JSON_FILENAME, CONFIG_FILENAME,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _svc_paths(svc, home):
    svc.home = home
    svc.lib_dir = home / LIB_DIR
    svc.vulkan_layer_dir = home / VULKAN_LAYER_DIR
    svc.config_dir = home / CONFIG_DIR
    svc.lib_file = svc.lib_dir / LIB_FILENAME
    svc.json_file = svc.vulkan_layer_dir / JSON_FILENAME
    svc.config_file = svc.config_dir / CONFIG_FILENAME
    svc.log_dir = home / ".local/share/omfg/logs"
    return svc


def make_plugin(home):
    plugin = Plugin()
    _svc_paths(plugin.installation_service, home)
    _svc_paths(plugin.configuration_service, home)
    return plugin


def make_base(home, mock_logger):
    svc = BaseService(logger=mock_logger)
    _svc_paths(svc, home)
    return svc


FAKE_MANIFEST = {
    "file_format_version": "1.0.0",
    "layer": {
        "name": "VK_LAYER_OMFG_rust",
        "type": "GLOBAL",
        "api_version": "1.3.250",
        "implementation_version": "1",
        "description": "test",
        "library_path": "./libVkLayer_OMFG_rust.so",
        "enable_environment": {"ENABLE_OMFG_RUST": "1"},
        "disable_environment": {"DISABLE_OMFG_RUST": "1"},
        "functions": {
            "vkNegotiateLoaderLayerInterfaceVersion":
                "vkNegotiateLoaderLayerInterfaceVersion"
        },
    },
}


def build_test_zip(tmp_path: Path) -> bytes:
    """Return bytes of a minimal omfg release zip."""
    d = tmp_path / "omfg-v0.1.0"
    d.mkdir(parents=True)
    (d / LIB_FILENAME).write_bytes(b"\x7fELF fake")
    (d / "shaders").mkdir()
    (d / "shaders" / "blend.frag.spv").write_bytes(b"SPV")
    (d / JSON_FILENAME).write_text(json.dumps(FAKE_MANIFEST))
    zip_path = tmp_path / "release.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for p in d.rglob("*"):
            zf.write(p, p.relative_to(tmp_path))
    return zip_path.read_bytes()


def _ctx_mock(data: bytes) -> MagicMock:
    """
    Context-manager mock whose .read(n) behaves like BytesIO(data).
    Correct for shutil.copyfileobj which calls read(chunk) in a loop.
    """
    buf = BytesIO(data)
    m = MagicMock()
    m.__enter__ = lambda s: s
    m.__exit__ = MagicMock(return_value=False)
    m.read.side_effect = buf.read      # read(n) returns b"" once exhausted
    return m


# ---------------------------------------------------------------------------
# BaseService: _remove_if_exists raises OSError
# ---------------------------------------------------------------------------

class TestBaseServiceEdgeCases:
    def test_remove_raises_on_oserror(self, patched_home, mock_logger):
        svc = make_base(patched_home, mock_logger)
        f = patched_home / "locked.txt"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x")

        def bad_unlink(self_path, missing_ok=False):
            raise OSError("permission denied")

        with patch.object(Path, "unlink", bad_unlink):
            with pytest.raises(OSError, match="permission denied"):
                svc._remove_if_exists(f)

    def test_atomic_write_cleans_up_temp_on_failure(self, patched_home, mock_logger):
        svc = make_base(patched_home, mock_logger)
        target = patched_home / "target.txt"
        target.parent.mkdir(parents=True, exist_ok=True)

        def bad_replace(self_path, other):
            raise OSError("rename failed")

        with patch.object(Path, "replace", bad_replace):
            with pytest.raises(OSError, match="rename failed"):
                svc._atomic_write(target, "data")

        # No stale temp files left
        assert list(target.parent.glob(".target.txt.*.tmp")) == []


# ---------------------------------------------------------------------------
# InstallationService: full install() orchestration
# (mocks _get_release_asset_url and _download so we test the orchestration
#  without touching the network; _extract_and_install tested separately)
# ---------------------------------------------------------------------------

class TestFullInstall:
    def test_install_orchestrates_all_steps(self, patched_home, tmp_path, mock_logger):
        from omfg.installation import InstallationService
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)

        zip_bytes = build_test_zip(tmp_path)

        # Stub: _get_release_asset_url returns a fake URL/name
        # Stub: _download writes the zip bytes to dest (bypasses shutil.copyfileobj)
        def fake_download(url, dest):
            dest.write_bytes(zip_bytes)

        with patch.object(svc, "_get_release_asset_url",
                          return_value=("http://x/a.zip", "omfg-v0.1.0-linux-amd64.zip")), \
             patch.object(svc, "_download", side_effect=fake_download):
            result = svc.install()

        assert result["success"] is True
        assert svc.lib_file.exists()
        assert svc.json_file.exists()
        assert svc.config_file.exists()
        assert (svc.config_dir / "omfg-wrapper.sh").exists()
        manifest = json.loads(svc.json_file.read_text())
        assert manifest["layer"]["library_path"] == str(svc.lib_file)

    def test_install_returns_error_on_get_release_failure(self, patched_home, mock_logger):
        from omfg.installation import InstallationService
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)

        with patch.object(svc, "_get_release_asset_url",
                          side_effect=OSError("network down")):
            result = svc.install()

        assert result["success"] is False
        assert "network down" in result["error"]

    def test_install_returns_error_on_download_failure(self, patched_home, mock_logger):
        from omfg.installation import InstallationService
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)

        with patch.object(svc, "_get_release_asset_url",
                          return_value=("http://x/a.zip", "a.zip")), \
             patch.object(svc, "_download",
                          side_effect=OSError("download failed")):
            result = svc.install()

        assert result["success"] is False
        assert "download failed" in result["error"]


# ---------------------------------------------------------------------------
# Plugin: lifecycle methods (_main, _unload, _uninstall, _migration)
# ---------------------------------------------------------------------------

class TestPluginLifecycle:
    def test_main_logs_loaded(self, patched_home, mock_decky):
        plugin = make_plugin(patched_home)
        run(plugin._main())
        mock_decky.logger.info.assert_called_once()

    def test_unload_logs(self, patched_home, mock_decky):
        plugin = make_plugin(patched_home)
        run(plugin._unload())
        mock_decky.logger.info.assert_called_once()

    def test_uninstall_calls_cleanup(self, patched_home, mock_decky):
        plugin = make_plugin(patched_home)
        with patch.object(plugin.installation_service, "cleanup_on_uninstall") as m:
            run(plugin._uninstall())
        m.assert_called_once()

    def test_migration_calls_all_migrate_functions(self, patched_home, mock_decky):
        mock_decky.DECKY_USER_HOME = str(patched_home)
        mock_decky.DECKY_HOME = str(patched_home / "homebrew")
        plugin = make_plugin(patched_home)
        run(plugin._migration())
        mock_decky.migrate_logs.assert_called_once()
        mock_decky.migrate_settings.assert_called_once()
        mock_decky.migrate_runtime.assert_called_once()


# ---------------------------------------------------------------------------
# config_schema: line 167 — the parse_toml line with no '=' but in [env]
# ---------------------------------------------------------------------------

class TestParseTomlEdgeCases:
    def test_line_with_no_equals_is_skipped(self):
        toml = "[env]\nthis line has no equals sign\nOMFG_LAYER_MODE = \"blend\"\n"
        result = ConfigurationManager.parse_toml(toml)
        assert result["OMFG_LAYER_MODE"] == "blend"

    def test_empty_key_after_strip_is_skipped(self):
        toml = "[env]\n = somevalue\n"
        result = ConfigurationManager.parse_toml(toml)
        # Should not crash, should return defaults
        assert result == ConfigurationManager.get_defaults()

    def test_single_quoted_strings_parsed(self):
        toml = "[env]\nOMFG_LAYER_MODE = 'passthrough'\n"
        result = ConfigurationManager.parse_toml(toml)
        assert result["OMFG_LAYER_MODE"] == "passthrough"


# ---------------------------------------------------------------------------
# installation.py:83-84  — lib_dir rmdir when empty after uninstall
# ---------------------------------------------------------------------------

class TestUninstallLibDirCleanup:
    def test_removes_empty_lib_dir(self, patched_home, mock_logger):
        from omfg.installation import InstallationService
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)
        # Create lib_dir with only the .so (so after removal it becomes empty)
        svc.lib_dir.mkdir(parents=True)
        svc.lib_file.write_bytes(b"x")
        svc.vulkan_layer_dir.mkdir(parents=True)
        svc.json_file.write_text("{}")
        result = svc.uninstall()
        assert result["success"] is True
        # lib_dir itself should be gone (was empty after .so removal)
        assert not svc.lib_dir.exists()
        assert str(svc.lib_dir) in result["removed_files"]

    def test_uninstall_outer_exception_returns_error(self, patched_home, mock_logger):
        from omfg.installation import InstallationService
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)

        def bad_remove(path):
            raise RuntimeError("unexpected failure")

        with patch.object(svc, "_remove_if_exists", side_effect=bad_remove):
            result = svc.uninstall()

        assert result["success"] is False
        assert result["error"] is not None


# ---------------------------------------------------------------------------
# installation.py:116-117  — check_installation: corrupt JSON in manifest
# installation.py:129-130  — check_installation: outer exception
# ---------------------------------------------------------------------------

class TestCheckInstallationExceptions:
    def test_corrupt_manifest_returns_empty_version(self, patched_home, mock_logger):
        from omfg.installation import InstallationService
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)
        svc.lib_dir.mkdir(parents=True)
        svc.lib_file.write_bytes(b"x")
        svc.vulkan_layer_dir.mkdir(parents=True)
        svc.json_file.write_text("THIS IS NOT JSON {{{{")   # corrupt
        result = svc.check_installation()
        assert result["installed"] is True
        assert result["installed_version"] == ""   # silently falls back

    def test_outer_exception_returns_error_dict(self, patched_home, mock_logger):
        from omfg.installation import InstallationService
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)

        def bad_exists(self_path):
            raise RuntimeError("stat failed")

        with patch.object(Path, "exists", bad_exists):
            result = svc.check_installation()

        assert result["installed"] is False
        assert result["error"] is not None


# ---------------------------------------------------------------------------
# base_service.py:71-72  — _atomic_write: unlink of temp file itself fails
# ---------------------------------------------------------------------------

class TestAtomicWriteTempUnlinkFails:
    def test_unlink_failure_in_cleanup_is_swallowed(self, patched_home, mock_logger):
        """If temp_path.unlink() raises OSError, _atomic_write should still re-raise
        the original exception without masking it."""
        svc = make_base(patched_home, mock_logger)
        target = patched_home / "target.txt"
        target.parent.mkdir(parents=True, exist_ok=True)

        call_count = [0]

        def flaky(self_path, other=None, missing_ok=False):
            call_count[0] += 1
            if call_count[0] == 1:
                raise OSError("rename failed")
            # Second call (unlink of temp): also raise to hit the inner except
            raise OSError("unlink also failed")

        # Patch both replace AND unlink so the inner except OSError: pass fires
        with patch.object(Path, "replace", flaky), \
             patch.object(Path, "unlink", flaky):
            with pytest.raises(OSError, match="rename failed"):
                svc._atomic_write(target, "data")


# ---------------------------------------------------------------------------
# plugin.py:32  — Plugin.install_omfg() delegates to installation_service
# plugin.py:129 — download_plugin_update: empty file branch
# ---------------------------------------------------------------------------

class TestPluginDelegation:
    def test_install_omfg_delegates_to_service(self, patched_home):
        plugin = make_plugin(patched_home)
        with patch.object(plugin.installation_service, "install",
                          return_value={"success": True, "message": "ok", "error": None}) as m:
            result = run(plugin.install_omfg())
        m.assert_called_once()
        assert result["success"] is True

    def test_download_plugin_update_empty_file_error(self, patched_home, mock_decky):
        plugin = make_plugin(patched_home)

        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = b""   # empty — triggers the "empty file" branch

        with patch("urllib.request.urlopen", return_value=mock_resp), \
             patch.object(Path, "home", return_value=patched_home):
            result = run(plugin.download_plugin_update("http://example.com/x.zip"))

        assert result["success"] is False
        assert "empty" in result["error"].lower()


# ---------------------------------------------------------------------------
# installation.py:85-86   — lib_dir.rmdir() OSError is swallowed
# ---------------------------------------------------------------------------

class TestUninstallLibDirRmdirFails:
    def test_lib_dir_rmdir_oserror_swallowed(self, patched_home, mock_logger):
        from omfg.installation import InstallationService
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)
        svc.lib_dir.mkdir(parents=True)
        svc.lib_file.write_bytes(b"x")
        svc.vulkan_layer_dir.mkdir(parents=True)
        svc.json_file.write_text("{}")

        original_rmdir = Path.rmdir

        def bad_rmdir(self_path):
            raise OSError("dir busy")

        # After lib_file is removed, lib_dir is empty and rmdir is called.
        # Patch rmdir to raise — the except OSError: pass branch fires.
        with patch.object(Path, "rmdir", bad_rmdir):
            result = svc.uninstall()

        # Uninstall still succeeds (the rmdir failure is swallowed)
        assert result["success"] is True


# ---------------------------------------------------------------------------
# installation.py:149-152 — cleanup_on_uninstall inner + outer exceptions
# ---------------------------------------------------------------------------

class TestCleanupOnUninstallExceptions:
    def test_inner_oserror_swallowed(self, patched_home, mock_logger):
        from omfg.installation import InstallationService
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)
        svc._ensure_directories()
        svc.lib_file.write_bytes(b"x")

        call_count = [0]
        original = svc._remove_if_exists

        def flaky_remove(path):
            call_count[0] += 1
            if call_count[0] == 1:
                raise OSError("first remove failed")
            return original(path)

        with patch.object(svc, "_remove_if_exists", side_effect=flaky_remove):
            # Should not raise — OSError is caught per-file
            svc.cleanup_on_uninstall()

    def test_outer_exception_logged(self, patched_home, mock_logger):
        from omfg.installation import InstallationService
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)

        def explode(*a, **kw):
            raise RuntimeError("catastrophic")

        with patch.object(svc, "_remove_if_exists", side_effect=explode):
            # Must not propagate — outer except catches and logs
            svc.cleanup_on_uninstall()

        mock_logger.error.assert_called()


# ---------------------------------------------------------------------------
# installation.py:176-178 — _download() body (urlopen + copyfileobj)
# ---------------------------------------------------------------------------

class TestDownloadMethod:
    def test_download_writes_zip_to_dest(self, patched_home, tmp_path, mock_logger):
        from omfg.installation import InstallationService
        from io import BytesIO
        svc = InstallationService(logger=mock_logger)
        _svc_paths(svc, patched_home)

        fake_data = b"PK fake zip content"
        dest = tmp_path / "download.zip"

        # BytesIO respects read(n) correctly — no infinite loop
        buf = BytesIO(fake_data)
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.side_effect = buf.read

        with patch("urllib.request.urlopen", return_value=mock_resp):
            svc._download("http://example.com/x.zip", dest)

        assert dest.exists()
        assert dest.read_bytes() == fake_data
