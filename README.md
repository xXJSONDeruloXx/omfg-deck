# OMFG Deck

A [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) plugin for the [OMFG (Open Multi Frame Generation)](https://github.com/xXJSONDeruloXx/omfg) Vulkan layer on Steam Deck.

## Features

- **One-click install** — downloads the latest OMFG release from GitHub and installs the Vulkan layer to the correct XDG paths
- **Live config editing** — all OMFG knobs surfaced in the plugin UI; changes are written to `~/.config/omfg/omfg-live.toml` and picked up by the layer within ~250 ms (no game restart needed)
- **Mode selector** — cycle through all OMFG frame-generation algorithm families (blend, reproject, optflow, multi, adaptive, …)
- **Debug view** — toggle the in-game diagnostic overlay
- **Per-game activation** — layer only activates when `ENABLE_OMFG_RUST=1` is set, so it is safe to install globally and enable per-game
- **Launch option clipboard** — one-tap copy of the Steam launch option string
- **Plugin update checker** — compare installed version against GitHub releases

## Quick start

1. Install via Decky Loader
2. Open the plugin and press **Install OMFG**
3. For each game you want frame generation on, add to its Steam **Launch Options**:

```
ENABLE_OMFG_RUST=1 OMFG_HOT_CONFIG_PATH=/home/deck/.config/omfg/omfg-live.toml %command%
```

4. Launch the game and tweak settings live from the plugin panel

## Installed file locations

| File | Path |
|---|---|
| Vulkan layer library | `~/.local/lib/omfg/libVkLayer_OMFG_rust.so` |
| Shader assets | `~/.local/lib/omfg/shaders/` |
| Layer manifest | `~/.local/share/vulkan/implicit_layer.d/VkLayer_OMFG_rust.json` |
| Hot-reload config | `~/.config/omfg/omfg-live.toml` |

## Building from source

```bash
pnpm install
just build   # produces out/OMFG.zip
```

## License

MIT
