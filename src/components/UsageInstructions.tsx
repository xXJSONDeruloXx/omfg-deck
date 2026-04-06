import { useState } from "react";
import { PanelSectionRow, ButtonItem, ToggleField } from "@decky/ui";
import { FaClipboard } from "react-icons/fa";
import { getLaunchOption, getWrapperLaunchOption } from "../api/omfgApi";
import { OmfgConfig, isMultiMode, isAdaptiveMode } from "../config/configSchema";

interface UsageInstructionsProps {
  config: OmfgConfig;
}

const CLIPBOARD_MODE_KEY = "omfg-clipboard-mode-wrapper";

function copyText(text: string) {
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(text).catch(() => execCopy(text));
  } else {
    execCopy(text);
  }
}

function execCopy(text: string) {
  const el = document.createElement("textarea");
  el.value = text;
  el.style.position = "fixed"; el.style.opacity = "0";
  document.body.appendChild(el); el.focus(); el.select();
  document.execCommand("copy");
  document.body.removeChild(el);
}

export function UsageInstructions({ config }: UsageInstructionsProps) {
  const [copied, setCopied] = useState(false);
  const [useWrapper, setUseWrapper] = useState(() => {
    try { return JSON.parse(localStorage.getItem(CLIPBOARD_MODE_KEY) ?? "false"); }
    catch { return false; }
  });

  const handleModeChange = (v: boolean) => {
    setUseWrapper(v);
    try { localStorage.setItem(CLIPBOARD_MODE_KEY, JSON.stringify(v)); } catch {}
  };

  const handleCopy = async () => {
    try {
      const result = useWrapper
        ? await getWrapperLaunchOption()
        : await getLaunchOption();
      if (result.success && result.launch_option) {
        copyText(result.launch_option);
        setCopied(true);
        setTimeout(() => setCopied(false), 2500);
      }
    } catch (e) {
      console.error("copy failed:", e);
    }
  };

  const showMulti = isMultiMode(config.OMFG_LAYER_MODE);
  const showAdaptive = isAdaptiveMode(config.OMFG_LAYER_MODE);

  const configSummary = [
    `• Mode: ${config.OMFG_LAYER_MODE}`,
    `• Debug: ${config.OMFG_DEBUG_VIEW}`,
    ...(showMulti ? [`• Generated frames: ${config.OMFG_MULTI_BLEND_COUNT}`] : []),
    ...(showAdaptive ? [
      `• Target FPS: ${config.OMFG_ADAPTIVE_MULTI_TARGET_FPS}`,
      `• Min/Max: ${config.OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES}–${config.OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES}`,
    ] : []),
    `• Present timing: ${config.OMFG_PRESENT_TIMING === 1 ? "on" : "off"}`,
    `• Benchmark: ${config.OMFG_BENCHMARK === 1 ? "on" : "off"}`,
  ].join("\n");

  return (
    <>
      <PanelSectionRow>
        <div style={{
          fontSize: "13px", fontWeight: "bold", marginTop: "12px", marginBottom: "6px",
          borderBottom: "1px solid rgba(255,255,255,0.2)", paddingBottom: "4px",
          textTransform: "uppercase", letterSpacing: "0.05em",
        }}>
          Usage
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label={useWrapper ? "Mode: Wrapper Script" : "Mode: Inline Env Vars"}
          description={
            useWrapper
              ? "/home/deck/.config/omfg/omfg-wrapper.sh %command%  — wrkaround vars applied automatically"
              : "Full env var string — workarounds prepended from Workarounds section"
          }
          checked={useWrapper}
          onChange={handleModeChange}
        />
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
        <div style={{
          fontSize: "12px", lineHeight: "1.55", opacity: 0.75, whiteSpace: "pre-wrap",
        }}>
          {configSummary}
        </div>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ fontSize: "11px", opacity: 0.55 }}>
          Config: <code>~/.config/omfg/omfg-live.toml</code>
          <br />Changes apply within ~250 ms — no restart needed.
        </div>
      </PanelSectionRow>
    </>
  );
}
