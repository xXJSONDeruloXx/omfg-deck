import { useState } from "react";
import { PanelSectionRow, ButtonItem } from "@decky/ui";
import { FaClipboard } from "react-icons/fa";
import { getLaunchOption } from "../api/omfgApi";
import { OmfgConfig } from "../config/configSchema";

interface UsageInstructionsProps {
  config: OmfgConfig;
}

export function UsageInstructions({ config }: UsageInstructionsProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      const result = await getLaunchOption();
      if (result.success && result.launch_option) {
        // Use the Steam/browser clipboard API if available, otherwise fall back
        if (typeof navigator !== "undefined" && navigator.clipboard) {
          await navigator.clipboard.writeText(result.launch_option);
        } else {
          // Fallback: show the string
          prompt("Copy this launch option:", result.launch_option);
        }
        setCopied(true);
        setTimeout(() => setCopied(false), 2500);
      }
    } catch (e) {
      console.error("Failed to copy launch option:", e);
    }
  };

  return (
    <>
      <PanelSectionRow>
        <div
          style={{
            fontSize: "13px",
            fontWeight: "bold",
            marginTop: "12px",
            marginBottom: "6px",
            borderBottom: "1px solid rgba(255,255,255,0.2)",
            paddingBottom: "4px",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          Usage
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ fontSize: "12px", lineHeight: "1.5", opacity: 0.85 }}>
          Add this to each game's{" "}
          <strong>Launch Options</strong> in Steam:
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            fontFamily: "monospace",
            fontSize: "11px",
            background: "rgba(0,0,0,0.35)",
            border: "1px solid rgba(255,255,255,0.15)",
            borderRadius: "4px",
            padding: "6px 8px",
            wordBreak: "break-all",
            lineHeight: "1.4",
            color: "#a8d8a8",
          }}
        >
          ENABLE_OMFG_RUST=1 OMFG_HOT_CONFIG_PATH=~/.config/omfg/omfg-live.toml %command%
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={handleCopy}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <FaClipboard />
            <div>{copied ? "Copied!" : "Copy Launch Option"}</div>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            fontSize: "12px",
            lineHeight: "1.45",
            opacity: 0.75,
          }}
        >
          Active mode: <strong>{config.OMFG_LAYER_MODE}</strong>
          <br />
          Debug view: <strong>{config.OMFG_DEBUG_VIEW}</strong>
          <br />
          Config: <code>~/.config/omfg/omfg-live.toml</code>
          <br />
          <em>Changes apply within ~250 ms — no game restart needed.</em>
        </div>
      </PanelSectionRow>
    </>
  );
}
