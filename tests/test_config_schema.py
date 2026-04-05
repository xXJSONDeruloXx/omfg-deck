"""
Tests for omfg.config_schema — ConfigurationManager.
"""
import pytest
from omfg.config_schema import ConfigurationManager, DEFAULTS, _TYPE_MAP
from omfg.constants import ALL_LAYER_MODES, DEBUG_VIEWS


# ---------------------------------------------------------------------------
# get_defaults
# ---------------------------------------------------------------------------

class TestGetDefaults:
    def test_returns_all_keys(self):
        d = ConfigurationManager.get_defaults()
        assert set(d.keys()) == set(_TYPE_MAP.keys())

    def test_returns_copy_not_singleton(self):
        a = ConfigurationManager.get_defaults()
        b = ConfigurationManager.get_defaults()
        a["OMFG_LAYER_MODE"] = "passthrough"
        assert b["OMFG_LAYER_MODE"] == DEFAULTS["OMFG_LAYER_MODE"]

    def test_default_mode_is_reproject_blend(self):
        assert ConfigurationManager.get_defaults()["OMFG_LAYER_MODE"] == "reproject-blend"

    def test_default_debug_view_is_off(self):
        assert ConfigurationManager.get_defaults()["OMFG_DEBUG_VIEW"] == "off"

    def test_all_numeric_defaults_are_correct_type(self):
        d = ConfigurationManager.get_defaults()
        for key, typ in _TYPE_MAP.items():
            assert isinstance(d[key], typ), f"{key} expected {typ}, got {type(d[key])}"


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_validates_full_valid_config(self):
        cfg = dict(DEFAULTS)
        result = ConfigurationManager.validate(cfg)
        assert result == cfg

    def test_fills_missing_keys_with_defaults(self):
        result = ConfigurationManager.validate({})
        assert result == ConfigurationManager.get_defaults()

    def test_coerces_string_int_to_int(self):
        result = ConfigurationManager.validate({"OMFG_REPROJECT_SEARCH_RADIUS": "3"})
        assert result["OMFG_REPROJECT_SEARCH_RADIUS"] == 3
        assert isinstance(result["OMFG_REPROJECT_SEARCH_RADIUS"], int)

    def test_coerces_string_float_to_float(self):
        result = ConfigurationManager.validate({"OMFG_REPROJECT_CONFIDENCE_SCALE": "5.5"})
        assert result["OMFG_REPROJECT_CONFIDENCE_SCALE"] == pytest.approx(5.5)

    def test_coerces_int_to_float(self):
        result = ConfigurationManager.validate({"OMFG_REPROJECT_CONFIDENCE_SCALE": 5})
        assert isinstance(result["OMFG_REPROJECT_CONFIDENCE_SCALE"], float)

    def test_invalid_value_falls_back_to_default(self):
        result = ConfigurationManager.validate({"OMFG_REPROJECT_SEARCH_RADIUS": "not-a-number"})
        assert result["OMFG_REPROJECT_SEARCH_RADIUS"] == DEFAULTS["OMFG_REPROJECT_SEARCH_RADIUS"]

    def test_unknown_keys_are_ignored(self):
        result = ConfigurationManager.validate({"UNKNOWN_KEY": 99})
        assert "UNKNOWN_KEY" not in result

    def test_validates_all_25_fields(self):
        result = ConfigurationManager.validate(ConfigurationManager.get_defaults())
        assert len(result) == 25


# ---------------------------------------------------------------------------
# generate_toml
# ---------------------------------------------------------------------------

class TestGenerateToml:
    def test_contains_env_section_header(self):
        toml = ConfigurationManager.generate_toml(ConfigurationManager.get_defaults())
        assert "[env]" in toml

    def test_contains_all_keys(self):
        toml = ConfigurationManager.generate_toml(ConfigurationManager.get_defaults())
        for key in _TYPE_MAP:
            assert key in toml

    def test_string_values_are_quoted(self):
        toml = ConfigurationManager.generate_toml(ConfigurationManager.get_defaults())
        assert 'OMFG_LAYER_MODE = "reproject-blend"' in toml
        assert 'OMFG_DEBUG_VIEW = "off"' in toml

    def test_int_values_are_unquoted(self):
        toml = ConfigurationManager.generate_toml(ConfigurationManager.get_defaults())
        assert "OMFG_REPROJECT_SEARCH_RADIUS = 2" in toml

    def test_float_values_are_unquoted(self):
        toml = ConfigurationManager.generate_toml(ConfigurationManager.get_defaults())
        assert "OMFG_REPROJECT_CONFIDENCE_SCALE = 4.0" in toml

    def test_output_is_string(self):
        assert isinstance(ConfigurationManager.generate_toml(ConfigurationManager.get_defaults()), str)

    def test_contains_comment_header(self):
        toml = ConfigurationManager.generate_toml(ConfigurationManager.get_defaults())
        assert toml.startswith("#")


# ---------------------------------------------------------------------------
# parse_toml
# ---------------------------------------------------------------------------

class TestParseToml:
    def test_parses_env_section(self):
        toml = '[env]\nOMFG_LAYER_MODE = "blend"\n'
        result = ConfigurationManager.parse_toml(toml)
        assert result["OMFG_LAYER_MODE"] == "blend"

    def test_parses_int(self):
        toml = "[env]\nOMFG_REPROJECT_SEARCH_RADIUS = 4\n"
        result = ConfigurationManager.parse_toml(toml)
        assert result["OMFG_REPROJECT_SEARCH_RADIUS"] == 4

    def test_parses_float(self):
        toml = "[env]\nOMFG_REPROJECT_CONFIDENCE_SCALE = 7.5\n"
        result = ConfigurationManager.parse_toml(toml)
        assert result["OMFG_REPROJECT_CONFIDENCE_SCALE"] == pytest.approx(7.5)

    def test_skips_comments(self):
        toml = "[env]\n# OMFG_LAYER_MODE = \"passthrough\"\n"
        result = ConfigurationManager.parse_toml(toml)
        assert result["OMFG_LAYER_MODE"] == DEFAULTS["OMFG_LAYER_MODE"]

    def test_ignores_keys_outside_env_section(self):
        toml = '[other]\nOMFG_LAYER_MODE = "passthrough"\n[env]\nOMFG_LAYER_MODE = "blend"\n'
        result = ConfigurationManager.parse_toml(toml)
        assert result["OMFG_LAYER_MODE"] == "blend"

    def test_returns_defaults_on_empty_input(self):
        result = ConfigurationManager.parse_toml("")
        assert result == ConfigurationManager.get_defaults()

    def test_returns_defaults_on_garbage_input(self):
        result = ConfigurationManager.parse_toml("not valid toml !!!@#$")
        assert result == ConfigurationManager.get_defaults()

    def test_ignores_unknown_keys(self):
        toml = "[env]\nUNKNOWN_KEY = 99\n"
        result = ConfigurationManager.parse_toml(toml)
        assert "UNKNOWN_KEY" not in result

    def test_invalid_int_value_falls_back_to_default(self):
        toml = "[env]\nOMFG_REPROJECT_SEARCH_RADIUS = bad\n"
        result = ConfigurationManager.parse_toml(toml)
        assert result["OMFG_REPROJECT_SEARCH_RADIUS"] == DEFAULTS["OMFG_REPROJECT_SEARCH_RADIUS"]


# ---------------------------------------------------------------------------
# Roundtrip: generate → parse
# ---------------------------------------------------------------------------

class TestRoundtrip:
    def test_defaults_roundtrip(self):
        original = ConfigurationManager.get_defaults()
        toml = ConfigurationManager.generate_toml(original)
        parsed = ConfigurationManager.parse_toml(toml)
        assert parsed == original

    def test_custom_values_roundtrip(self):
        cfg = ConfigurationManager.get_defaults()
        cfg["OMFG_LAYER_MODE"] = "optflow-blend"
        cfg["OMFG_REPROJECT_SEARCH_RADIUS"] = 5
        cfg["OMFG_REPROJECT_CONFIDENCE_SCALE"] = 6.5
        cfg["OMFG_MULTI_BLEND_COUNT"] = 3
        toml = ConfigurationManager.generate_toml(cfg)
        parsed = ConfigurationManager.parse_toml(toml)
        assert parsed["OMFG_LAYER_MODE"] == "optflow-blend"
        assert parsed["OMFG_REPROJECT_SEARCH_RADIUS"] == 5
        assert parsed["OMFG_REPROJECT_CONFIDENCE_SCALE"] == pytest.approx(6.5)
        assert parsed["OMFG_MULTI_BLEND_COUNT"] == 3

    @pytest.mark.parametrize("mode", ALL_LAYER_MODES)
    def test_all_modes_roundtrip(self, mode):
        cfg = ConfigurationManager.get_defaults()
        cfg["OMFG_LAYER_MODE"] = mode
        parsed = ConfigurationManager.parse_toml(ConfigurationManager.generate_toml(cfg))
        assert parsed["OMFG_LAYER_MODE"] == mode

    @pytest.mark.parametrize("view", DEBUG_VIEWS)
    def test_all_debug_views_roundtrip(self, view):
        cfg = ConfigurationManager.get_defaults()
        cfg["OMFG_DEBUG_VIEW"] = view
        parsed = ConfigurationManager.parse_toml(ConfigurationManager.generate_toml(cfg))
        assert parsed["OMFG_DEBUG_VIEW"] == view
