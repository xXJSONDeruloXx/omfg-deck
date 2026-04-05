# omfg-deck Gap Implementation v0.1.2

## Items to implement

### Python backend
1. **`config_schema.py`**: Add 12 missing env vars to OmfgConfig/DEFAULTS/_TYPE_MAP:
   - Hot-reload: `OMFG_ADAPTIVE_MULTI_INTERVAL_THRESHOLD_MS` (float,1.0), `OMFG_BFI_HOLD_MS` (int,8), `OMFG_VISUAL_HOLD_MS` (int,8), `OMFG_BLEND_ORIGINAL_PRESENT_FIRST` (int,0), `OMFG_COPY_ORIGINAL_PRESENT_FIRST` (int,0), `OMFG_HISTORY_COPY_FREEZE_HISTORY` (int,0), `OMFG_PRESENT_WAIT_TIMEOUT_NS` (int,5000000000), `OMFG_BENCHMARK_LABEL` (str,"live")
   - Startup-scoped: `OMFG_SWAPCHAIN_IMAGE_BUMP_OVERRIDE` (int,0), `OMFG_CREATE_DEVICE_DEBUG` (int,0), `OMFG_CREATE_DEVICE_APPEND_TIMING_EXTENSIONS` (int,0), `OMFG_CREATE_DEVICE_APPEND_TIMING_FEATURES` (int,0)

2. **`plugin.py`**: Add `get_layer_log(lines)`, `set_layer_enabled(enabled)`, `get_layer_enabled()`

3. **`installation.py`**: Update `_write_wrapper_script()` to source `~/.config/omfg/omfg.env` and respect `OMFG_DISABLE_LAYER`

4. **`constants.py`**: Add `ENV_FILENAME = "omfg.env"`, `LOG_FILENAME = "omfg.log"`

### TypeScript frontend
5. **`configSchema.ts`**: Add all 12 new fields + helpers `isBfiMode`, `isBlendMode`, `isCopyMode`, `isHistoryCopyMode`, `isVisualMode`

6. **`omfgApi.ts`**: Add `getLayerLog`, `setLayerEnabled`, `getLayerEnabled` callables

7. **`ConfigurationSection.tsx`**: Add all missing UI controls with context visibility + startup-scoped section with "⚠ Requires game restart" label

8. **`LogViewer.tsx`**: New component — "View Log" button fetches last 50 lines, renders in scrollable panel

9. **`Content.tsx`**: Add global layer enable/disable toggle above InstallationButton

### Tests
10. Update tests for new schema fields (37 → ~40 fields), new plugin methods

### Build & release
11. `pnpm build` → `cli/decky plugin build` → `gh release create v0.1.2`

## Working directory
`/Users/kurt/Developer/omfg-deck`
