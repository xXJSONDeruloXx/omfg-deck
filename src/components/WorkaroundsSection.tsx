import { useState, useEffect } from "react";
import { PanelSectionRow, ToggleField, SliderField, ButtonItem } from "@decky/ui";
import { RiArrowDownSFill, RiArrowUpSFill } from "react-icons/ri";
import { WorkaroundState } from "../hooks/useWorkarounds";

const STORAGE_KEY = "omfg-workarounds-collapsed";

interface Props {
  workarounds: WorkaroundState;
  onToggle: (key: keyof WorkaroundState, enabled: boolean) => Promise<void>;
  onSetInt: (key: keyof WorkaroundState, value: number) => Promise<void>;
}

export function WorkaroundsSection({ workarounds, onToggle, onSetInt }: Props) {
  const [collapsed, setCollapsed] = useState(() => {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "true"); }
    catch { return true; }
  });

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(collapsed)); } catch {}
  }, [collapsed]);

  return (
    <>
      <PanelSectionRow>
        <div style={{
          fontSize: "14px", fontWeight: "bold", marginTop: "8px", marginBottom: "6px",
          borderBottom: "1px solid rgba(255,255,255,0.2)", paddingBottom: "3px", color: "white",
        }}>
          Workarounds
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" bottomSeparator={collapsed ? "standard" : "none"}
          onClick={() => setCollapsed((c: boolean) => !c)}>
          {collapsed
            ? <RiArrowDownSFill style={{ transform: "translate(0,-13px)", fontSize: "1.5em" }} />
            : <RiArrowUpSFill  style={{ transform: "translate(0,-12px)", fontSize: "1.5em" }} />}
        </ButtonItem>
      </PanelSectionRow>

      {!collapsed && (
        <>
          <PanelSectionRow>
            <ToggleField
              label="Disable vSync"
              description="MESA_VK_WSI_PRESENT_MODE=immediate — recommended for frame gen, prevents compositor sync interfering with frame insertion"
              checked={workarounds.mesa_immediate}
              onChange={(v) => onToggle("mesa_immediate", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label={`Base FPS Cap${workarounds.dxvk_frame_rate > 0 ? ` (${workarounds.dxvk_frame_rate} FPS)` : " (Off)"}`}
              description="DXVK_FRAME_RATE — cap base game fps before multiplier (DirectX games). 0 = disabled"
              value={workarounds.dxvk_frame_rate}
              min={0} max={60} step={1}
              showValue
              onChange={(v) => onSetInt("dxvk_frame_rate", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <ToggleField
              label="Disable vkbasalt"
              description="DISABLE_VKBASALT=1 — disables vkBasalt layer which can conflict with OMFG (Reshade, some Decky plugins)"
              checked={workarounds.disable_vkbasalt}
              disabled={workarounds.force_enable_vkbasalt}
              onChange={(v) => onToggle("disable_vkbasalt", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <ToggleField
              label="Force Enable vkbasalt"
              description="ENABLE_VKBASALT=1 — force-enable vkBasalt to fix framepacing in game mode"
              checked={workarounds.force_enable_vkbasalt}
              disabled={workarounds.disable_vkbasalt}
              onChange={(v) => onToggle("force_enable_vkbasalt", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <ToggleField
              label="Enable Gamescope WSI"
              description="Re-enable Gamescope WSI layer — disabled by default as it conflicts with frame gen. Requires game restart."
              checked={workarounds.enable_gamescope_wsi}
              onChange={(v) => onToggle("enable_gamescope_wsi", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <ToggleField
              label="WoW64 for 32-bit Games"
              description="PROTON_USE_WOW64=1 — use with ProtonGE to fix crashes in 32-bit games"
              checked={workarounds.enable_wow64}
              onChange={(v) => onToggle("enable_wow64", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <ToggleField
              label="Disable Steam Deck Mode"
              description="SteamDeck=0 — unlocks hidden settings in some games that behave differently on Deck"
              checked={workarounds.disable_steamdeck}
              onChange={(v) => onToggle("disable_steamdeck", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <ToggleField
              label="MangoHud Workaround"
              description="MANGOHUD=1 — transparent overlay, sometimes fixes 2X multiplier issues in game mode"
              checked={workarounds.mangohud}
              onChange={(v) => onToggle("mangohud", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <ToggleField
              label="Enable Zink (OpenGL → Vulkan)"
              description="Sets __GLX_VENDOR_LIBRARY_NAME=mesa, MESA_LOADER_DRIVER_OVERRIDE=zink, GALLIUM_DRIVER=zink — for OpenGL games"
              checked={workarounds.enable_zink}
              onChange={(v) => onToggle("enable_zink", v)}
            />
          </PanelSectionRow>
        </>
      )}
    </>
  );
}
