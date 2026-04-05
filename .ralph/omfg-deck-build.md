# omfg-deck Decky Plugin – Feature-Parity Build

## Goal
Build `omfg-deck` as a full-featured Decky Loader plugin mirroring `decky-lsfg-vk` but targeting the **OMFG Vulkan frame-generation layer** (`xXJSONDeruloXx/omfg`).

## Release asset
- GitHub: `xXJSONDeruloXx/omfg`, latest release asset `omfg-v0.1.0-linux-amd64.zip`
- Zip contents: `libVkLayer_OMFG_rust.so`, `VkLayer_OMFG_rust.json` (relative library_path), `shaders/`, `omfg-wrapper.sh`, `omfg-live.toml`

## Installation layout on deck
- `~/.local/lib/omfg/libVkLayer_OMFG_rust.so`
- `~/.local/lib/omfg/shaders/`  (shaders relative to .so)
- `~/.local/share/vulkan/implicit_layer.d/VkLayer_OMFG_rust.json`  (library_path updated to absolute)
- `~/.config/omfg/omfg-live.toml`  (hot-reload config, polled every 250ms)

## Layer activation
- Layer only runs when `ENABLE_OMFG_RUST=1` in env
- Per-game launch option: `ENABLE_OMFG_RUST=1 OMFG_HOT_CONFIG_PATH=/home/deck/.config/omfg/omfg-live.toml %command%`
- Plugin provides a clipboard button for that string

## Config schema (maps to `[env]` section of omfg-live.toml)
Primary: OMFG_LAYER_MODE (string, many modes), OMFG_DEBUG_VIEW (string)
Multi/adaptive: OMFG_MULTI_BLEND_COUNT (int), OMFG_ADAPTIVE_MULTI_TARGET_FPS (int), OMFG_ADAPTIVE_MULTI_MIN/MAX_GENERATED_FRAMES (int)
Reproject: OMFG_REPROJECT_SEARCH_RADIUS, OMFG_REPROJECT_PATCH_RADIUS, OMFG_REPROJECT_CONFIDENCE_SCALE, OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS (floats/ints)
Optical flow: OMFG_OPTICAL_FLOW_SEARCH_RADIUS, OMFG_OPTICAL_FLOW_PATCH_RADIUS, OMFG_OPTICAL_FLOW_LEVELS (ints)
Advanced: OMFG_BFI_PERIOD (int), OMFG_PRESENT_TIMING (0/1), OMFG_BENCHMARK (0/1)

## Feature checklist
- [ ] plugin.json and package.json updated for omfg
- [ ] py_modules/omfg/ package: constants, types, base_service, config_schema, installation, configuration, plugin
- [ ] main.py → thin wrapper importing Plugin from omfg
- [ ] Download from GitHub releases (no bundled zip), extract layer files to correct locations
- [ ] Update VkLayer_OMFG_rust.json library_path to absolute on install
- [ ] Write omfg-live.toml with default config on install
- [ ] TypeScript API layer (omfgApi.ts) matching all backend callables
- [ ] TypeScript config schema (configSchema.ts) matching Python schema
- [ ] Hooks: useInstallationStatus, useOmfgConfig, useInstallationActions
- [ ] Components: Content, StatusDisplay, InstallationButton, ConfigurationSection (with mode dropdown, debug view, sliders), UsageInstructions (shows launch option), PluginUpdateChecker
- [ ] index.tsx updated with OMFG branding + icon
- [ ] Builds to out/ successfully (pnpm build)
- [ ] Progressively committed as features are added

## Working directory
`/Users/kurt/Developer/omfg-deck`

## Reference
`/Users/kurt/Developer/decky-lossless-scaling-vk` – full lsfg-vk plugin for patterns/parity
