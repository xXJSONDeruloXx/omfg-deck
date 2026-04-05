"""
Tests for omfg.installation — InstallationService.
"""
import json
import zipfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from omfg.installation import InstallationService
from omfg.config_schema import ConfigurationManager
from omfg.constants import (
    LIB_FILENAME, JSON_FILENAME, SHADERS_DIR, WRAPPER_FILENAME, CONFIG_FILENAME,
    LIB_DIR, VULKAN_LAYER_DIR, CONFIG_DIR,
)

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
    },
}


def make_service(tmp_home, mock_logger):
    svc = InstallationService(logger=mock_logger)
    svc.home = tmp_home
    svc.lib_dir = tmp_home / LIB_DIR
    svc.vulkan_layer_dir = tmp_home / VULKAN_LAYER_DIR
    svc.config_dir = tmp_home / CONFIG_DIR
    svc.lib_file = svc.lib_dir / LIB_FILENAME
    svc.json_file = svc.vulkan_layer_dir / JSON_FILENAME
    svc.config_file = svc.config_dir / CONFIG_FILENAME
    svc.log_dir = tmp_home / ".local/share/omfg/logs"
    return svc


def build_test_zip(tmp_path: Path) -> Path:
    """Build a minimal release zip mimicking the real omfg release layout."""
    release_dir = tmp_path / "omfg-v0.1.0"
    release_dir.mkdir()
    (release_dir / LIB_FILENAME).write_bytes(b"\x7fELF fake binary")
    shaders = release_dir / SHADERS_DIR
    shaders.mkdir()
    (shaders / "blend.frag.spv").write_bytes(b"SPIR-V fake")
    manifest_path = release_dir / JSON_FILENAME
    manifest_path.write_text(json.dumps(FAKE_MANIFEST))

    zip_path = tmp_path / "omfg-v0.1.0-linux-amd64.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for p in release_dir.rglob("*"):
            zf.write(p, p.relative_to(tmp_path))
    return zip_path


# ---------------------------------------------------------------------------
# check_installation
# ---------------------------------------------------------------------------

class TestCheckInstallation:
    def test_not_installed_when_no_files(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        r = svc.check_installation()
        assert r["installed"] is False
        assert r["lib_exists"] is False
        assert r["json_exists"] is False
        assert r["config_exists"] is False
        assert r["wrapper_exists"] is False
        assert r["installed_version"] == ""
        assert r["error"] is None

    def test_installed_when_both_layer_files_present(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.lib_dir.mkdir(parents=True)
        svc.lib_file.write_bytes(b"fake")
        svc.vulkan_layer_dir.mkdir(parents=True)
        svc.json_file.write_text(json.dumps(FAKE_MANIFEST))
        r = svc.check_installation()
        assert r["installed"] is True
        assert r["lib_exists"] is True
        assert r["json_exists"] is True

    def test_not_installed_when_only_lib_present(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.lib_dir.mkdir(parents=True)
        svc.lib_file.write_bytes(b"fake")
        r = svc.check_installation()
        assert r["installed"] is False

    def test_not_installed_when_only_json_present(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.vulkan_layer_dir.mkdir(parents=True)
        svc.json_file.write_text(json.dumps(FAKE_MANIFEST))
        r = svc.check_installation()
        assert r["installed"] is False

    def test_extracts_version_from_manifest(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.lib_dir.mkdir(parents=True)
        svc.lib_file.write_bytes(b"fake")
        svc.vulkan_layer_dir.mkdir(parents=True)
        svc.json_file.write_text(json.dumps(FAKE_MANIFEST))
        r = svc.check_installation()
        assert r["installed_version"] == "1"

    def test_config_exists_flag(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.config_dir.mkdir(parents=True)
        svc.config_file.write_text("[env]\n")
        r = svc.check_installation()
        assert r["config_exists"] is True

    def test_wrapper_exists_flag(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.config_dir.mkdir(parents=True)
        (svc.config_dir / WRAPPER_FILENAME).write_text("#!/bin/bash\n")
        r = svc.check_installation()
        assert r["wrapper_exists"] is True

    def test_returns_correct_paths(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        r = svc.check_installation()
        assert r["lib_path"] == str(svc.lib_file)
        assert r["json_path"] == str(svc.json_file)


# ---------------------------------------------------------------------------
# _extract_and_install
# ---------------------------------------------------------------------------

class TestExtractAndInstall:
    def test_installs_so_file(self, patched_home, tmp_path, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        zip_path = build_test_zip(tmp_path)
        svc._extract_and_install(zip_path)
        assert svc.lib_file.exists()
        assert svc.lib_file.read_bytes() == b"\x7fELF fake binary"

    def test_so_file_is_executable(self, patched_home, tmp_path, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        zip_path = build_test_zip(tmp_path)
        svc._extract_and_install(zip_path)
        import stat
        mode = stat.S_IMODE(svc.lib_file.stat().st_mode)
        assert mode & 0o111  # executable bits set

    def test_installs_shaders(self, patched_home, tmp_path, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        zip_path = build_test_zip(tmp_path)
        svc._extract_and_install(zip_path)
        assert (svc.lib_dir / SHADERS_DIR / "blend.frag.spv").exists()

    def test_manifest_library_path_updated_to_absolute(self, patched_home, tmp_path, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        zip_path = build_test_zip(tmp_path)
        svc._extract_and_install(zip_path)
        manifest = json.loads(svc.json_file.read_text())
        assert manifest["layer"]["library_path"] == str(svc.lib_file)
        assert manifest["layer"]["library_path"].startswith("/")

    def test_manifest_other_fields_preserved(self, patched_home, tmp_path, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        zip_path = build_test_zip(tmp_path)
        svc._extract_and_install(zip_path)
        manifest = json.loads(svc.json_file.read_text())
        assert manifest["layer"]["name"] == "VK_LAYER_OMFG_rust"
        assert manifest["layer"]["enable_environment"] == {"ENABLE_OMFG_RUST": "1"}

    def test_overwrites_existing_shaders(self, patched_home, tmp_path, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        old_shaders = svc.lib_dir / SHADERS_DIR
        old_shaders.mkdir()
        (old_shaders / "old.spv").write_bytes(b"old")
        zip_path = build_test_zip(tmp_path)
        svc._extract_and_install(zip_path)
        assert not (old_shaders / "old.spv").exists()
        assert (old_shaders / "blend.frag.spv").exists()


# ---------------------------------------------------------------------------
# _write_default_config
# ---------------------------------------------------------------------------

class TestWriteDefaultConfig:
    def test_creates_config_file(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc._write_default_config()
        assert svc.config_file.exists()

    def test_config_contains_default_mode(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc._write_default_config()
        content = svc.config_file.read_text()
        assert 'OMFG_LAYER_MODE = "reproject-blend"' in content

    def test_does_not_overwrite_existing_config(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc.config_file.write_text("# custom config\n")
        svc._write_default_config()
        assert "# custom config" in svc.config_file.read_text()


# ---------------------------------------------------------------------------
# _write_wrapper_script
# ---------------------------------------------------------------------------

class TestWriteWrapperScript:
    def test_creates_wrapper_file(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc._write_wrapper_script()
        assert (svc.config_dir / WRAPPER_FILENAME).exists()

    def test_wrapper_is_executable(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc._write_wrapper_script()
        import stat
        mode = stat.S_IMODE((svc.config_dir / WRAPPER_FILENAME).stat().st_mode)
        assert mode & 0o111

    def test_wrapper_contains_enable_env(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc._write_wrapper_script()
        content = (svc.config_dir / WRAPPER_FILENAME).read_text()
        assert "ENABLE_OMFG_RUST=1" in content

    def test_wrapper_contains_config_path(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc._write_wrapper_script()
        content = (svc.config_dir / WRAPPER_FILENAME).read_text()
        assert str(svc.config_file) in content

    def test_wrapper_execs_args(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc._write_wrapper_script()
        content = (svc.config_dir / WRAPPER_FILENAME).read_text()
        assert 'exec "$@"' in content


# ---------------------------------------------------------------------------
# uninstall
# ---------------------------------------------------------------------------

class TestUninstall:
    def test_removes_layer_files(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.lib_dir.mkdir(parents=True)
        svc.lib_file.write_bytes(b"fake")
        svc.vulkan_layer_dir.mkdir(parents=True)
        svc.json_file.write_text("{}")
        result = svc.uninstall()
        assert result["success"] is True
        assert not svc.lib_file.exists()
        assert not svc.json_file.exists()

    def test_removes_shaders_dir(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.lib_dir.mkdir(parents=True)
        shaders = svc.lib_dir / SHADERS_DIR
        shaders.mkdir()
        (shaders / "x.spv").write_bytes(b"spv")
        result = svc.uninstall()
        assert result["success"] is True
        assert not shaders.exists()

    def test_preserves_config_file(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc.config_file.write_text("[env]\n")
        svc.uninstall()
        assert svc.config_file.exists()

    def test_reports_nothing_when_already_clean(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        result = svc.uninstall()
        assert result["success"] is True
        assert result["removed_files"] is None

    def test_removed_files_list_populated(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.lib_dir.mkdir(parents=True)
        svc.lib_file.write_bytes(b"x")
        svc.vulkan_layer_dir.mkdir(parents=True)
        svc.json_file.write_text("{}")
        result = svc.uninstall()
        assert len(result["removed_files"]) >= 2


# ---------------------------------------------------------------------------
# cleanup_on_uninstall
# ---------------------------------------------------------------------------

class TestCleanupOnUninstall:
    def test_removes_all_managed_files(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc._ensure_directories()
        svc.lib_file.write_bytes(b"x")
        svc.json_file.write_text("{}")
        svc.config_file.write_text("[env]\n")
        (svc.lib_dir / SHADERS_DIR).mkdir()
        svc.cleanup_on_uninstall()
        assert not svc.lib_file.exists()
        assert not svc.json_file.exists()

    def test_does_not_raise_when_nothing_installed(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.cleanup_on_uninstall()  # should not raise


# ---------------------------------------------------------------------------
# _get_release_asset_url fallback
# ---------------------------------------------------------------------------

class TestGetReleaseAssetUrl:
    def _make_api_response(self, assets, tag="v0.1.0"):
        import io, json as json_mod
        body = json_mod.dumps({"tag_name": tag, "assets": assets}).encode()
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = body
        return mock_resp

    def test_finds_matching_asset(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        assets = [{"name": "omfg-v0.1.0-linux-amd64.zip", "browser_download_url": "http://example.com/a.zip"}]
        resp = self._make_api_response(assets)
        with patch("urllib.request.urlopen", return_value=resp):
            url, name = svc._get_release_asset_url()
        assert url == "http://example.com/a.zip"
        assert name == "omfg-v0.1.0-linux-amd64.zip"

    def test_fallback_url_when_no_matching_asset(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        resp = self._make_api_response([], tag="v0.2.0")
        with patch("urllib.request.urlopen", return_value=resp):
            url, name = svc._get_release_asset_url()
        assert "v0.2.0" in url
        assert name.endswith(".zip")
