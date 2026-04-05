# omfg-deck Decky Plugin – Feature-Parity Build

## Status: COMPLETE ✅

All items delivered across 4 progressive commits. Builds cleanly to `out/OMFG.zip`.

## Feature checklist
- [x] plugin.json and package.json updated for omfg
- [x] py_modules/omfg/ package: constants, types, base_service, config_schema, installation, configuration, plugin
- [x] main.py → thin wrapper importing Plugin from omfg
- [x] Download from GitHub releases (no bundled zip), extract layer files to correct locations
- [x] Update VkLayer_OMFG_rust.json library_path to absolute on install
- [x] Write omfg-live.toml with default config on install
- [x] Write omfg-wrapper.sh on install
- [x] TypeScript API layer (omfgApi.ts) matching all backend callables
- [x] TypeScript config schema (configSchema.ts) matching Python schema
- [x] Hooks: useInstallationStatus, useOmfgConfig, useInstallationActions
- [x] Components: Content, StatusDisplay, InstallationButton, ConfigurationSection, UsageInstructions, PluginUpdateChecker, GitHubButton
- [x] index.tsx updated with OMFG branding + FaLayerGroup icon
- [x] Builds to out/OMFG.zip successfully
- [x] 4 progressive commits
