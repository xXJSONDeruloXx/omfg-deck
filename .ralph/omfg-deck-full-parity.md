# omfg-deck Full Feature Parity (no profile mgmt, no fp16)

## What to implement

### Workarounds — 8 missing toggles + DXVK slider
All go into `omfg.env` and are **translated in the wrapper script** AND in the generated launch option string:
- `DXVK_FRAME_RATE` — int slider 0-60 (0=off), base fps cap
- `PROTON_USE_WOW64=1` — 32-bit ProtonGE fix
- `SteamDeck=0` — disable Steam Deck mode
- `MANGOHUD=1` — transparent overlay, fixes 2X multiplier
- `DISABLE_VKBASALT=1` — already exists but only in launch opt; add to wrapper + mutex with force_enable
- `ENABLE_VKBASALT=1` — force enable, mutex with disable_vkbasalt
- Gamescope WSI disable: `ENABLE_GAMESCOPE_WSI=0 DXVK_HDR=0` — default OFF (disable by default, toggle re-enables)
- Zink: `__GLX_VENDOR_LIBRARY_NAME=mesa MESA_LOADER_DRIVER_OVERRIDE=zink GALLIUM_DRIVER=zink`

### Wrapper script hardening
- Translate all `WORKAROUND_*` flags into actual env vars in the script body
- Add explicit `VK_INSTANCE_LAYERS=VK_LAYER_OMFG_rust` + `VK_LAYER_PATH=~/.local/lib/omfg`
- Add `PRESSURE_VESSEL_FILESYSTEMS_RW` for Proton container access

### UX: Collapsible sections
- Config section: collapsible, state saved in localStorage (default expanded)
- Workarounds section: collapsible, state saved in localStorage (default collapsed like lsfg-vk)

### NerdStuff modal
- Button in plugin panel opens modal
- Shows raw `omfg-live.toml` content + raw wrapper script content
- Copy button for each

### Smart clipboard (two modes)
- Toggle/tabs: "Wrapper" (`/home/deck/.config/omfg/omfg-wrapper.sh %command%`) vs "Inline" (full env var string)
- Both include active workarounds

### Backend (`plugin.py`)
- Expand `get_workarounds()` / `set_workaround(key, value: str)` for all 9 keys (value is string for int support)
- `get_launch_option()` — include all active workaround vars
- `get_config_file_content()` → raw toml
- `get_wrapper_script_content()` → raw wrapper

### Tests
- Cover all new backend methods to maintain 100% coverage

## Working directory
`/Users/kurt/Developer/omfg-deck`
