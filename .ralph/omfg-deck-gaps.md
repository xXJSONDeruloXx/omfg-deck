# omfg-deck Gap Fix Loop

## Confirmed gaps to fix

### TypeScript / Frontend
1. **ConfigurationSection: `CycleField` → `DropdownItem`** (proper Decky gamepad-navigable dropdown for mode + debug view)
2. **ConfigurationSection: missing all advanced reproject sliders** (5 missing: DISOCCLUSION_SCALE, HOLE_FILL_RADIUS, GRADIENT_CONFIDENCE_WEIGHT, CHROMA_WEIGHT, AMBIGUITY_SCALE)
3. **ConfigurationSection: missing optical flow sliders** (3 missing: PATCH_RADIUS, CONFIDENCE_SCALE, MOTION_PENALTY)
4. **ConfigurationSection: missing `OMFG_PRESENT_WAIT` toggle** in diagnostics
5. **ConfigurationSection: add "Reset to Defaults" button** wired to backend
6. **`omfgApi.ts`: add `resetOmfgConfig` callable**
7. **`useOmfgConfig`: add `resetConfig` function**
8. **`InstallationStatus` interface: add `config_exists`, `wrapper_exists`, `installed_version` fields**
9. **`StatusDisplay`: show config file presence status**
10. **`defaults.txt`: replace placeholder with OMFG-specific content**

### Python / Backend
11. **`check_installation` returns dead `version` variable** — remove dead code, include `config_exists`, `wrapper_exists`, `installed_version` in response
12. **`InstallationCheckResponse` TypedDict**: add `config_exists`, `wrapper_exists`, `installed_version`
13. **Add `reset_config` method** to `plugin.py` and `configuration.py`

## Working directory
`/Users/kurt/Developer/omfg-deck`
