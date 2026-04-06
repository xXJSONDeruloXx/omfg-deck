import { PanelSectionRow, ToggleField } from "@decky/ui";
import { WorkaroundState } from "../hooks/useWorkarounds";

interface WorkaroundsSectionProps {
  workarounds: WorkaroundState;
  onToggle: (key: keyof WorkaroundState, enabled: boolean) => Promise<void>;
}

export function WorkaroundsSection({ workarounds, onToggle }: WorkaroundsSectionProps) {
  return (
    <>
      <PanelSectionRow>
        <div style={{
          fontSize: "12px", fontWeight: "bold", marginTop: "10px", marginBottom: "2px",
          borderBottom: "1px solid rgba(255,255,255,0.18)", paddingBottom: "3px",
          textTransform: "uppercase", letterSpacing: "0.06em", opacity: 0.85,
        }}>
          Workarounds
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Disable vSync"
          description={
            "Adds MESA_VK_WSI_PRESENT_MODE=immediate to launch option. " +
            "Recommended — prevents compositor sync from interfering with frame insertion. " +
            "May cause screen tearing in rare cases."
          }
          checked={workarounds.mesa_immediate}
          onChange={(v) => onToggle("mesa_immediate", v)}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Disable vkbasalt"
          description={
            "Adds DISABLE_VKBASALT=1 to launch option. " +
            "Enable if you see black screens or artifacts — vkbasalt can conflict with frame generation."
          }
          checked={workarounds.disable_vkbasalt}
          onChange={(v) => onToggle("disable_vkbasalt", v)}
        />
      </PanelSectionRow>

      {(workarounds.mesa_immediate || workarounds.disable_vkbasalt) && (
        <PanelSectionRow>
          <div style={{
            fontSize: "11px", opacity: 0.6, lineHeight: "1.4",
            fontFamily: "monospace",
            background: "rgba(0,0,0,0.25)", borderRadius: "4px",
            padding: "4px 6px",
          }}>
            Active:{" "}
            {[
              workarounds.mesa_immediate && "MESA_VK_WSI_PRESENT_MODE=immediate",
              workarounds.disable_vkbasalt && "DISABLE_VKBASALT=1",
            ].filter(Boolean).join("  ")}
          </div>
        </PanelSectionRow>
      )}
    </>
  );
}
