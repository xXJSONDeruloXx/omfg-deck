"""
Constants for the omfg-deck plugin.
"""

# Layer file names
LIB_FILENAME = "libVkLayer_OMFG_rust.so"
JSON_FILENAME = "VkLayer_OMFG_rust.json"
CONFIG_FILENAME = "omfg-live.toml"
WRAPPER_FILENAME = "omfg-wrapper.sh"
SHADERS_DIR = "shaders"

# Directory paths (relative to $HOME)
LIB_DIR = ".local/lib/omfg"
VULKAN_LAYER_DIR = ".local/share/vulkan/implicit_layer.d"
CONFIG_DIR = ".config/omfg"
LOG_DIR = ".local/share/omfg/logs"

# GitHub release
GITHUB_REPO = "xXJSONDeruloXx/omfg"
GITHUB_API_URL = "https://api.github.com/repos/xXJSONDeruloXx/omfg/releases/latest"
RELEASE_ASSET_SUFFIX = "linux-amd64.zip"

# Layer identity
LAYER_NAME = "VK_LAYER_OMFG_rust"
LAYER_ENABLE_ENV = "ENABLE_OMFG_RUST"
LAYER_DISABLE_ENV = "DISABLE_OMFG_RUST"
HOT_CONFIG_ENV = "OMFG_HOT_CONFIG_PATH"

# Available layer modes grouped by family
LAYER_MODES_UTILITY = [
    "passthrough", "clear", "bfi", "copy", "history-copy"
]
LAYER_MODES_SINGLE = [
    "blend", "adaptive-blend", "search-blend", "search-adaptive-blend",
    "reproject-blend", "reproject-adaptive-blend", "optflow-blend"
]
LAYER_MODES_MULTI = [
    "multi-blend", "adaptive-multi-blend", "reproject-multi-blend",
    "reproject-adaptive-multi-blend", "optflow-multi-blend", "optflow-adaptive-multi-blend"
]
ALL_LAYER_MODES = LAYER_MODES_UTILITY + LAYER_MODES_SINGLE + LAYER_MODES_MULTI

# Available debug views
DEBUG_VIEWS = [
    "off", "motion", "confidence", "ambiguity", "disocclusion", "hole-fill", "fallback"
]
