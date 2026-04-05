import { useState } from "react";
import { PanelSectionRow, ButtonItem } from "@decky/ui";
import { FaClipboard } from "react-icons/fa";
import { getLaunchOption } from "../api/omfgApi";
import { OmfgConfig, isMultiMode, isAdaptiveMode } from "../config/configSchema";

interface UsageInstructionsProps {
  config: OmfgConfig;
}

export function UsageInstructions({ config }: UsageInstructionsProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      const result = await getLaunchOption();
      if (result.success && result.launch_option) {
        if (typeof navigator !== "undefined" && navigator.clipboard) {
          await navigator.clipboard.writeText(result.launch_option);
        }
        setCopied(true);
        setTimeout(() => setCopied(false), 2500);
      }
    } catch (e) {
      console.error("Failed to copy launch option:", e);
    }
  };

  const showMulti = isMultiMode(config.OMFG_LAYER_MODE);
  const showAdaptive = isAdaptiveMode(config.OMFG_LAYER_MODE);

  const configSummaryLines = [
    `• Mode: ${config.OMFG_LAYER_MODE}`,
    `• Debug: ${config.OMFG_DEBUG_VIEW}`,
    ...(showMulti ? [`• Generated frames: ${config.OMFG_MULTI_BLEND_COUNT}`] : []),
    ...(showAdaptive
      ? [
          `• Target FPS: ${config.OMFG_ADAPTIVE_MULTI_TARGET_FPS}`,
          `• Generated min/max: ${config.OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES}–${config.OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES}`,
        ]
      : []),
    `• Present timing: ${config.OMFG_PRESENT_TIMING === 1 ? "on" : "off"}`,
    `• Benchmark: ${config.OMFG_BENCHMARK === 1 ? "on" : "off"}`,
  ];

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
          Add to each game's <strong>Launch Options</strong>:
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            fontFamily: "monospace",
            fontSize: "10px",
            background: "rgba(0,0,0,0.35)",
            border: "1px solid rgba(255,255,255,0.15)",
            borderRadius: "4px",
            padding: "6px 8px",
            wordBreak: "break-all",
            lineHeight: "1.5",
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
            <div>{copied ? "✓ Copied!" : "Copy Launch Option"}</div>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <div
          style={{
            fontSize: "12px",
            lineHeight: "1.55",
            opacity: 0.75,
            whiteSpace: "pre-wrap",
          }}
        >
          {configSummaryLines.join("\n")}
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ fontSize: "11px", opacity: 0.55, marginTop: "4px" }}>
          Config file: <code>~/.config/omfg/omfg-live.toml</code>
          <br />
          Changes apply within ~250 ms — no restart needed.
        </div>
      </PanelSectionRow>
    </>
  );
}
