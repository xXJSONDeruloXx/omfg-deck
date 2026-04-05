"""
Configuration schema for the OMFG layer.

The omfg-live.toml file uses an [env] section where keys are the raw
OMFG_* environment variable names.  This module defines defaults, TOML
serialisation and simple regex-based parsing – no external TOML library
required.
"""

from typing import TypedDict, Dict, Any, cast


# ---------------------------------------------------------------------------
# Type definition (keys match the env-var names exactly)
# ---------------------------------------------------------------------------

class OmfgConfig(TypedDict):
    OMFG_LAYER_MODE: str
    OMFG_DEBUG_VIEW: str
    # Reproject
    OMFG_REPROJECT_SEARCH_RADIUS: int
    OMFG_REPROJECT_PATCH_RADIUS: int
    OMFG_REPROJECT_CONFIDENCE_SCALE: float
    OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS: float
    OMFG_REPROJECT_DISOCCLUSION_SCALE: float
    OMFG_REPROJECT_HOLE_FILL_STRENGTH: float
    OMFG_REPROJECT_HOLE_FILL_RADIUS: int
    OMFG_REPROJECT_GRADIENT_CONFIDENCE_WEIGHT: float
    OMFG_REPROJECT_CHROMA_WEIGHT: float
    OMFG_REPROJECT_AMBIGUITY_SCALE: float
    # Optical flow
    OMFG_OPTICAL_FLOW_SEARCH_RADIUS: int
    OMFG_OPTICAL_FLOW_PATCH_RADIUS: int
    OMFG_OPTICAL_FLOW_LEVELS: int
    OMFG_OPTICAL_FLOW_CONFIDENCE_SCALE: float
    OMFG_OPTICAL_FLOW_MOTION_PENALTY: float
    # Multi / adaptive
    OMFG_MULTI_BLEND_COUNT: int
    OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES: int
    OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES: int
    OMFG_ADAPTIVE_MULTI_TARGET_FPS: int
    OMFG_ADAPTIVE_MULTI_INTERVAL_THRESHOLD_MS: float
    # BFI / visual timing
    OMFG_BFI_PERIOD: int
    OMFG_BFI_HOLD_MS: int
    OMFG_VISUAL_HOLD_MS: int
    # Mode-specific flags
    OMFG_BLEND_ORIGINAL_PRESENT_FIRST: int
    OMFG_COPY_ORIGINAL_PRESENT_FIRST: int
    OMFG_HISTORY_COPY_FREEZE_HISTORY: int
    # Diagnostics
    OMFG_PRESENT_TIMING: int
    OMFG_PRESENT_WAIT: int
    OMFG_PRESENT_WAIT_TIMEOUT_NS: int
    OMFG_BENCHMARK: int
    OMFG_BENCHMARK_LABEL: str
    # Startup-scoped (need game restart to apply)
    OMFG_SWAPCHAIN_IMAGE_BUMP_OVERRIDE: int
    OMFG_CREATE_DEVICE_DEBUG: int
    OMFG_CREATE_DEVICE_APPEND_TIMING_EXTENSIONS: int
    OMFG_CREATE_DEVICE_APPEND_TIMING_FEATURES: int


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULTS: OmfgConfig = cast(OmfgConfig, {
    "OMFG_LAYER_MODE": "reproject-blend",
    "OMFG_DEBUG_VIEW": "off",
    # Reproject
    "OMFG_REPROJECT_SEARCH_RADIUS": 2,
    "OMFG_REPROJECT_PATCH_RADIUS": 1,
    "OMFG_REPROJECT_CONFIDENCE_SCALE": 4.0,
    "OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS": 0.75,
    "OMFG_REPROJECT_DISOCCLUSION_SCALE": 2.0,
    "OMFG_REPROJECT_HOLE_FILL_STRENGTH": 0.85,
    "OMFG_REPROJECT_HOLE_FILL_RADIUS": 2,
    "OMFG_REPROJECT_GRADIENT_CONFIDENCE_WEIGHT": 8.0,
    "OMFG_REPROJECT_CHROMA_WEIGHT": 0.3,
    "OMFG_REPROJECT_AMBIGUITY_SCALE": 6.0,
    # Optical flow
    "OMFG_OPTICAL_FLOW_SEARCH_RADIUS": 2,
    "OMFG_OPTICAL_FLOW_PATCH_RADIUS": 1,
    "OMFG_OPTICAL_FLOW_LEVELS": 3,
    "OMFG_OPTICAL_FLOW_CONFIDENCE_SCALE": 4.0,
    "OMFG_OPTICAL_FLOW_MOTION_PENALTY": 0.01,
    # Multi / adaptive
    "OMFG_MULTI_BLEND_COUNT": 2,
    "OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES": 0,
    "OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES": 2,
    "OMFG_ADAPTIVE_MULTI_TARGET_FPS": 120,
    "OMFG_ADAPTIVE_MULTI_INTERVAL_THRESHOLD_MS": 1.0,
    # BFI / visual timing
    "OMFG_BFI_PERIOD": 1,
    "OMFG_BFI_HOLD_MS": 8,
    "OMFG_VISUAL_HOLD_MS": 8,
    # Mode-specific flags
    "OMFG_BLEND_ORIGINAL_PRESENT_FIRST": 0,
    "OMFG_COPY_ORIGINAL_PRESENT_FIRST": 0,
    "OMFG_HISTORY_COPY_FREEZE_HISTORY": 0,
    # Diagnostics
    "OMFG_PRESENT_TIMING": 0,
    "OMFG_PRESENT_WAIT": 0,
    "OMFG_PRESENT_WAIT_TIMEOUT_NS": 5_000_000_000,
    "OMFG_BENCHMARK": 0,
    "OMFG_BENCHMARK_LABEL": "live",
    # Startup-scoped
    "OMFG_SWAPCHAIN_IMAGE_BUMP_OVERRIDE": 0,
    "OMFG_CREATE_DEVICE_DEBUG": 0,
    "OMFG_CREATE_DEVICE_APPEND_TIMING_EXTENSIONS": 0,
    "OMFG_CREATE_DEVICE_APPEND_TIMING_FEATURES": 0,
})

# Type map: key → Python type constructor
_TYPE_MAP: Dict[str, type] = {
    "OMFG_LAYER_MODE": str,
    "OMFG_DEBUG_VIEW": str,
    "OMFG_REPROJECT_SEARCH_RADIUS": int,
    "OMFG_REPROJECT_PATCH_RADIUS": int,
    "OMFG_REPROJECT_CONFIDENCE_SCALE": float,
    "OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS": float,
    "OMFG_REPROJECT_DISOCCLUSION_SCALE": float,
    "OMFG_REPROJECT_HOLE_FILL_STRENGTH": float,
    "OMFG_REPROJECT_HOLE_FILL_RADIUS": int,
    "OMFG_REPROJECT_GRADIENT_CONFIDENCE_WEIGHT": float,
    "OMFG_REPROJECT_CHROMA_WEIGHT": float,
    "OMFG_REPROJECT_AMBIGUITY_SCALE": float,
    "OMFG_OPTICAL_FLOW_SEARCH_RADIUS": int,
    "OMFG_OPTICAL_FLOW_PATCH_RADIUS": int,
    "OMFG_OPTICAL_FLOW_LEVELS": int,
    "OMFG_OPTICAL_FLOW_CONFIDENCE_SCALE": float,
    "OMFG_OPTICAL_FLOW_MOTION_PENALTY": float,
    "OMFG_MULTI_BLEND_COUNT": int,
    "OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES": int,
    "OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES": int,
    "OMFG_ADAPTIVE_MULTI_TARGET_FPS": int,
    "OMFG_ADAPTIVE_MULTI_INTERVAL_THRESHOLD_MS": float,
    "OMFG_BFI_PERIOD": int,
    "OMFG_BFI_HOLD_MS": int,
    "OMFG_VISUAL_HOLD_MS": int,
    "OMFG_BLEND_ORIGINAL_PRESENT_FIRST": int,
    "OMFG_COPY_ORIGINAL_PRESENT_FIRST": int,
    "OMFG_HISTORY_COPY_FREEZE_HISTORY": int,
    "OMFG_PRESENT_TIMING": int,
    "OMFG_PRESENT_WAIT": int,
    "OMFG_PRESENT_WAIT_TIMEOUT_NS": int,
    "OMFG_BENCHMARK": int,
    "OMFG_BENCHMARK_LABEL": str,
    "OMFG_SWAPCHAIN_IMAGE_BUMP_OVERRIDE": int,
    "OMFG_CREATE_DEVICE_DEBUG": int,
    "OMFG_CREATE_DEVICE_APPEND_TIMING_EXTENSIONS": int,
    "OMFG_CREATE_DEVICE_APPEND_TIMING_FEATURES": int,
}


# ---------------------------------------------------------------------------
# ConfigurationManager
# ---------------------------------------------------------------------------

class ConfigurationManager:

    @staticmethod
    def get_defaults() -> OmfgConfig:
        return dict(DEFAULTS)  # type: ignore[return-value]

    @staticmethod
    def validate(config: Dict[str, Any]) -> OmfgConfig:
        result = ConfigurationManager.get_defaults()
        for key, typ in _TYPE_MAP.items():
            if key in config:
                try:
                    result[key] = typ(config[key])  # type: ignore[literal-required]
                except (ValueError, TypeError):
                    pass
        return result

    @staticmethod
    def generate_toml(config: OmfgConfig) -> str:
        """Serialise config to the [env] TOML format used by the layer."""
        lines = [
            "# OMFG hot-reload config — managed by omfg-deck Decky plugin",
            "# The layer polls this file every ~250 ms.",
            "",
            "[env]",
            "",
        ]
        for key, typ in _TYPE_MAP.items():
            value = config.get(key, DEFAULTS[key])  # type: ignore[literal-required]
            if typ is str:
                lines.append(f'{key} = "{value}"')
            else:
                lines.append(f"{key} = {value}")
        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def parse_toml(content: str) -> OmfgConfig:
        """Parse [env] section from TOML content (no external library)."""
        config = ConfigurationManager.get_defaults()
        in_env = False
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('[') and line.endswith(']'):
                in_env = (line[1:-1].strip() == 'env')
                continue
            if not in_env:
                continue
            if '=' not in line:
                continue
            key, _, val = line.partition('=')
            key = key.strip()
            val = val.strip()
            if not key:
                continue
            if key not in _TYPE_MAP:
                continue
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            try:
                config[key] = _TYPE_MAP[key](val)  # type: ignore[literal-required]
            except (ValueError, TypeError):
                pass
        return config
