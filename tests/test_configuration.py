"""
Tests for omfg.configuration — ConfigurationService.
"""
import pytest
from pathlib import Path
from omfg.configuration import ConfigurationService
from omfg.config_schema import ConfigurationManager, DEFAULTS


def make_service(tmp_home, mock_logger):
    svc = ConfigurationService(logger=mock_logger)
    svc.home = tmp_home
    svc.config_dir = tmp_home / ".config" / "omfg"
    svc.config_file = svc.config_dir / "omfg-live.toml"
    return svc


# ---------------------------------------------------------------------------
# get_config
# ---------------------------------------------------------------------------

class TestGetConfig:
    def test_returns_defaults_when_file_missing(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        result = svc.get_config()
        assert result["success"] is True
        assert result["config"] == ConfigurationManager.get_defaults()
        assert "not found" in result["message"]

    def test_reads_existing_file(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.config_dir.mkdir(parents=True)
        svc.config_file.write_text('[env]\nOMFG_LAYER_MODE = "blend"\n')
        result = svc.get_config()
        assert result["success"] is True
        assert result["config"]["OMFG_LAYER_MODE"] == "blend"

    def test_returns_defaults_on_parse_failure(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.config_dir.mkdir(parents=True)
        svc.config_file.write_text("[env]\nOMFG_REPROJECT_SEARCH_RADIUS = bad\n")
        result = svc.get_config()
        assert result["success"] is True
        assert result["config"]["OMFG_REPROJECT_SEARCH_RADIUS"] == DEFAULTS["OMFG_REPROJECT_SEARCH_RADIUS"]

    def test_error_on_unreadable_file(self, patched_home, mock_logger, monkeypatch):
        svc = make_service(patched_home, mock_logger)
        svc.config_dir.mkdir(parents=True)
        svc.config_file.write_text("x")
        monkeypatch.setattr(Path, "read_text", lambda *a, **kw: (_ for _ in ()).throw(OSError("perm denied")))
        result = svc.get_config()
        assert result["success"] is False
        assert result["error"] is not None


# ---------------------------------------------------------------------------
# update_config
# ---------------------------------------------------------------------------

class TestUpdateConfig:
    def test_writes_toml_file(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        cfg = ConfigurationManager.get_defaults()
        cfg["OMFG_LAYER_MODE"] = "passthrough"
        result = svc.update_config(cfg)
        assert result["success"] is True
        assert svc.config_file.exists()
        content = svc.config_file.read_text()
        assert 'OMFG_LAYER_MODE = "passthrough"' in content

    def test_creates_config_dir_if_missing(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        assert not svc.config_dir.exists()
        svc.update_config(ConfigurationManager.get_defaults())
        assert svc.config_dir.exists()

    def test_returns_validated_config(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        result = svc.update_config({"OMFG_MULTI_BLEND_COUNT": "3"})
        assert result["success"] is True
        assert result["config"]["OMFG_MULTI_BLEND_COUNT"] == 3

    def test_error_when_write_fails(self, patched_home, mock_logger, monkeypatch):
        svc = make_service(patched_home, mock_logger)
        monkeypatch.setattr(svc, "_atomic_write", lambda *a, **kw: (_ for _ in ()).throw(OSError("disk full")))
        result = svc.update_config(ConfigurationManager.get_defaults())
        assert result["success"] is False
        assert "disk full" in result["error"]


# ---------------------------------------------------------------------------
# update_field
# ---------------------------------------------------------------------------

class TestUpdateField:
    def test_updates_single_field(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        # Write initial config
        svc.update_config(ConfigurationManager.get_defaults())
        result = svc.update_field("OMFG_LAYER_MODE", "copy")
        assert result["success"] is True
        readback = svc.get_config()
        assert readback["config"]["OMFG_LAYER_MODE"] == "copy"

    def test_preserves_other_fields(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.update_config(ConfigurationManager.get_defaults())
        svc.update_field("OMFG_MULTI_BLEND_COUNT", 4)
        cfg = svc.get_config()["config"]
        assert cfg["OMFG_MULTI_BLEND_COUNT"] == 4
        assert cfg["OMFG_LAYER_MODE"] == DEFAULTS["OMFG_LAYER_MODE"]

    def test_update_field_when_file_missing_uses_defaults(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        result = svc.update_field("OMFG_DEBUG_VIEW", "motion")
        assert result["success"] is True
        cfg = svc.get_config()["config"]
        assert cfg["OMFG_DEBUG_VIEW"] == "motion"


# ---------------------------------------------------------------------------
# reset_config
# ---------------------------------------------------------------------------

class TestResetConfig:
    def test_resets_to_defaults(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        cfg = ConfigurationManager.get_defaults()
        cfg["OMFG_LAYER_MODE"] = "passthrough"
        svc.update_config(cfg)
        result = svc.reset_config()
        assert result["success"] is True
        assert result["config"]["OMFG_LAYER_MODE"] == DEFAULTS["OMFG_LAYER_MODE"]

    def test_creates_backup_of_existing_config(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.update_config(ConfigurationManager.get_defaults())
        svc.reset_config()
        backup = svc.config_file.with_suffix(".toml.bak")
        assert backup.exists()

    def test_no_backup_when_config_missing(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        result = svc.reset_config()
        assert result["success"] is True
        backup = svc.config_file.with_suffix(".toml.bak")
        assert not backup.exists()

    def test_reset_config_is_readable(self, patched_home, mock_logger):
        svc = make_service(patched_home, mock_logger)
        svc.reset_config()
        result = svc.get_config()
        assert result["success"] is True
        assert result["config"] == ConfigurationManager.get_defaults()

    def test_error_propagated_on_write_failure(self, patched_home, mock_logger, monkeypatch):
        svc = make_service(patched_home, mock_logger)
        monkeypatch.setattr(svc, "_atomic_write", lambda *a, **kw: (_ for _ in ()).throw(OSError("no space")))
        result = svc.reset_config()
        assert result["success"] is False
        assert result["error"] is not None


# ---------------------------------------------------------------------------
# Roundtrip: write → read
# ---------------------------------------------------------------------------

class TestConfigRoundtrip:
    @pytest.mark.parametrize("field,value", [
        ("OMFG_LAYER_MODE", "optflow-blend"),
        ("OMFG_DEBUG_VIEW", "motion"),
        ("OMFG_REPROJECT_SEARCH_RADIUS", 5),
        ("OMFG_MULTI_BLEND_COUNT", 3),
        ("OMFG_ADAPTIVE_MULTI_TARGET_FPS", 90),
        ("OMFG_PRESENT_TIMING", 1),
        ("OMFG_BENCHMARK", 1),
    ])
    def test_field_roundtrip(self, patched_home, mock_logger, field, value):
        svc = make_service(patched_home, mock_logger)
        cfg = ConfigurationManager.get_defaults()
        cfg[field] = value
        svc.update_config(cfg)
        result = svc.get_config()
        assert result["config"][field] == value
