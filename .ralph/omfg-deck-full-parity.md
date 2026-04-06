# omfg-deck Full Feature Parity (no profile mgmt, no fp16)

## Status: COMPLETE ✅

All items implemented, tested, built, and released as v0.1.4.

## Release
https://github.com/xXJSONDeruloXx/omfg-deck/releases/tag/v0.1.4

## Summary
- 9 workaround toggles (MESA immediate, DXVK_FRAME_RATE slider, DISABLE/FORCE_ENABLE vkbasalt mutex, Gamescope WSI off-by-default, WoW64, SteamDeck=0, MangoHud, Zink)
- All workarounds translated in wrapper script body AND launch option string
- Wrapper hardened: VK_INSTANCE_LAYERS, VK_LAYER_PATH, PRESSURE_VESSEL_FILESYSTEMS_RW
- Config section collapsible (default expanded), Workarounds collapsed by default — localStorage persisted
- NerdStuff modal: raw omfg-live.toml + omfg-wrapper.sh with copy buttons
- Smart clipboard: toggle between inline env-var and wrapper-script launch option
- 213 tests, 100% backend coverage, CI green
