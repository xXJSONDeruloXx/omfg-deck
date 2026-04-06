import { useState, useEffect } from "react";
import { PanelSectionRow, ToggleField, SliderField, DropdownItem, ButtonItem, TextField } from "@decky/ui";
import { RiArrowDownSFill, RiArrowUpSFill } from "react-icons/ri";
import {
  OmfgConfig,
  ALL_LAYER_MODES,
  DEBUG_VIEWS,
  isMultiMode,
  isAdaptiveMode,
  isReprojectMode,
  isOptflowMode,
  isBfiMode,
  isBlendMode,
  isCopyMode,
  isHistoryCopyMode,
  isVisualMode,
} from "../config/configSchema";

const MODE_OPTIONS_FLAT = ALL_LAYER_MODES.map((m) => ({ data: m, label: m }));
const DEBUG_OPTIONS = DEBUG_VIEWS.map((v) => ({ data: v, label: v }));

function SectionHeader({ title, sub }: { title: string; sub?: string }) {
  return (
    <PanelSectionRow>
      <div style={{
        fontSize: "12px", fontWeight: "bold", marginTop: "10px", marginBottom: "2px",
        borderBottom: "1px solid rgba(255,255,255,0.18)", paddingBottom: "3px",
        textTransform: "uppercase", letterSpacing: "0.06em", opacity: 0.85,
      }}>
        {title}
        {sub && <span style={{ fontSize: "10px", fontWeight: "normal", marginLeft: "6px", opacity: 0.6 }}>{sub}</span>}
      </div>
    </PanelSectionRow>
  );
}

interface Props {
  config: OmfgConfig;
  onFieldChange: (key: keyof OmfgConfig, value: OmfgConfig[keyof OmfgConfig]) => Promise<void>;
  onReset: () => Promise<unknown>;
}

const CONFIG_STORAGE_KEY = "omfg-config-collapsed";

export function ConfigurationSection({ config, onFieldChange, onReset }: Props) {
  const [collapsed, setCollapsed] = useState(() => {
    try { return JSON.parse(localStorage.getItem(CONFIG_STORAGE_KEY) ?? "false"); }
    catch { return false; }
  });

  useEffect(() => {
    try { localStorage.setItem(CONFIG_STORAGE_KEY, JSON.stringify(collapsed)); } catch {}
  }, [collapsed]);

  const mode = config.OMFG_LAYER_MODE;
  const showMulti      = isMultiMode(mode);
  const showAdaptive   = isAdaptiveMode(mode);
  const showReproject  = isReprojectMode(mode);
  const showOptflow    = isOptflowMode(mode);
  const showBfi        = isBfiMode(mode);
  const showBlend      = isBlendMode(mode);
  const showCopy       = isCopyMode(mode);
  const showHistCopy   = isHistoryCopyMode(mode);
  const showVisual     = isVisualMode(mode);

  return (
    <>
      {/* ── Config header + collapse ────────────────── */}
      <PanelSectionRow>
        <div style={{
          fontSize: "14px", fontWeight: "bold", marginTop: "8px", marginBottom: "6px",
          borderBottom: "1px solid rgba(255,255,255,0.2)", paddingBottom: "3px", color: "white",
        }}>
          Config
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
      {/* ── Mode ────────────────────────────────────── */}
      <SectionHeader title="Mode" />
      <PanelSectionRow>
        <DropdownItem label="Layer Mode" description="Frame generation algorithm family"
          rgOptions={MODE_OPTIONS_FLAT} selectedOption={config.OMFG_LAYER_MODE}
          onChange={(opt) => onFieldChange("OMFG_LAYER_MODE", opt.data)} />
      </PanelSectionRow>
      <PanelSectionRow>
        <DropdownItem label="Debug View" description="In-game diagnostic overlay (off = normal)"
          rgOptions={DEBUG_OPTIONS} selectedOption={config.OMFG_DEBUG_VIEW}
          onChange={(opt) => onFieldChange("OMFG_DEBUG_VIEW", opt.data)} />
      </PanelSectionRow>

      {/* ── Multi / Adaptive ────────────────────────── */}
      {(showMulti || showAdaptive) && (
        <>
          <SectionHeader title="Multi / Adaptive" />
          {showMulti && (
            <PanelSectionRow>
              <SliderField label="Generated Frames" description="Frames to insert per real frame"
                value={config.OMFG_MULTI_BLEND_COUNT} min={1} max={4} step={1}
                notchCount={4} notchLabels={[{notchIndex:0,label:"1"},{notchIndex:1,label:"2"},{notchIndex:2,label:"3"},{notchIndex:3,label:"4"}]}
                showValue resetValue={2}
                onChange={(v) => onFieldChange("OMFG_MULTI_BLEND_COUNT", v)} />
            </PanelSectionRow>
          )}
          {showAdaptive && (<>
            <PanelSectionRow>
              <SliderField label="Target FPS" description="Adaptive controller target frame rate"
                value={config.OMFG_ADAPTIVE_MULTI_TARGET_FPS} min={30} max={240} step={5}
                showValue resetValue={120}
                onChange={(v) => onFieldChange("OMFG_ADAPTIVE_MULTI_TARGET_FPS", v)} />
            </PanelSectionRow>
            <PanelSectionRow>
              <SliderField label="Min Generated Frames" description="Minimum generated frames when adapting"
                value={config.OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES} min={0} max={3} step={1}
                showValue resetValue={0}
                onChange={(v) => onFieldChange("OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES", v)} />
            </PanelSectionRow>
            <PanelSectionRow>
              <SliderField label="Max Generated Frames" description="Maximum generated frames when adapting"
                value={config.OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES} min={1} max={4} step={1}
                showValue resetValue={2}
                onChange={(v) => onFieldChange("OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES", v)} />
            </PanelSectionRow>
            <PanelSectionRow>
              <SliderField label="Interval Threshold (ms)" description="Adaptive controller debounce interval"
                value={config.OMFG_ADAPTIVE_MULTI_INTERVAL_THRESHOLD_MS} min={0.1} max={10.0} step={0.1}
                showValue resetValue={1.0}
                onChange={(v) => onFieldChange("OMFG_ADAPTIVE_MULTI_INTERVAL_THRESHOLD_MS", v)} />
            </PanelSectionRow>
          </>)}
        </>
      )}

      {/* ── Reprojection ────────────────────────────── */}
      {showReproject && (<>
        <SectionHeader title="Reprojection" />
        <PanelSectionRow><SliderField label="Search Radius" description="Motion search radius (higher = more accurate, slower)"
          value={config.OMFG_REPROJECT_SEARCH_RADIUS} min={1} max={6} step={1} showValue resetValue={2}
          onChange={(v) => onFieldChange("OMFG_REPROJECT_SEARCH_RADIUS", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Patch Radius" description="Comparison patch half-size"
          value={config.OMFG_REPROJECT_PATCH_RADIUS} min={1} max={4} step={1} showValue resetValue={1}
          onChange={(v) => onFieldChange("OMFG_REPROJECT_PATCH_RADIUS", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Confidence Scale" description="Motion confidence threshold multiplier"
          value={config.OMFG_REPROJECT_CONFIDENCE_SCALE} min={1.0} max={10.0} step={0.5} showValue resetValue={4.0}
          onChange={(v) => onFieldChange("OMFG_REPROJECT_CONFIDENCE_SCALE", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Disocclusion Current Bias" description="Blend bias toward current frame in disoccluded regions"
          value={config.OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS} min={0.0} max={1.0} step={0.05} showValue resetValue={0.75}
          onChange={(v) => onFieldChange("OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Disocclusion Scale" description="Disocclusion region detection sensitivity"
          value={config.OMFG_REPROJECT_DISOCCLUSION_SCALE} min={0.5} max={6.0} step={0.25} showValue resetValue={2.0}
          onChange={(v) => onFieldChange("OMFG_REPROJECT_DISOCCLUSION_SCALE", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Hole Fill Strength" description="Strength of hole-filling in disoccluded areas"
          value={config.OMFG_REPROJECT_HOLE_FILL_STRENGTH} min={0.0} max={1.0} step={0.05} showValue resetValue={0.85}
          onChange={(v) => onFieldChange("OMFG_REPROJECT_HOLE_FILL_STRENGTH", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Hole Fill Radius" description="Spatial radius for hole-fill sampling"
          value={config.OMFG_REPROJECT_HOLE_FILL_RADIUS} min={1} max={6} step={1} showValue resetValue={2}
          onChange={(v) => onFieldChange("OMFG_REPROJECT_HOLE_FILL_RADIUS", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Gradient Confidence Weight" description="Edge-gradient contribution to confidence score"
          value={config.OMFG_REPROJECT_GRADIENT_CONFIDENCE_WEIGHT} min={0.0} max={16.0} step={0.5} showValue resetValue={8.0}
          onChange={(v) => onFieldChange("OMFG_REPROJECT_GRADIENT_CONFIDENCE_WEIGHT", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Chroma Weight" description="Color/chroma contribution to motion matching"
          value={config.OMFG_REPROJECT_CHROMA_WEIGHT} min={0.0} max={1.0} step={0.05} showValue resetValue={0.3}
          onChange={(v) => onFieldChange("OMFG_REPROJECT_CHROMA_WEIGHT", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Ambiguity Scale" description="Multi-candidate motion ambiguity sensitivity"
          value={config.OMFG_REPROJECT_AMBIGUITY_SCALE} min={1.0} max={12.0} step={0.5} showValue resetValue={6.0}
          onChange={(v) => onFieldChange("OMFG_REPROJECT_AMBIGUITY_SCALE", v)} /></PanelSectionRow>
      </>)}

      {/* ── Optical Flow ────────────────────────────── */}
      {showOptflow && (<>
        <SectionHeader title="Optical Flow" />
        <PanelSectionRow><SliderField label="Search Radius" description="Optical flow search radius"
          value={config.OMFG_OPTICAL_FLOW_SEARCH_RADIUS} min={1} max={6} step={1} showValue resetValue={2}
          onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_SEARCH_RADIUS", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Patch Radius" description="Patch comparison half-size"
          value={config.OMFG_OPTICAL_FLOW_PATCH_RADIUS} min={1} max={4} step={1} showValue resetValue={1}
          onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_PATCH_RADIUS", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Pyramid Levels" description="Multi-scale pyramid depth"
          value={config.OMFG_OPTICAL_FLOW_LEVELS} min={1} max={5} step={1} showValue resetValue={3}
          onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_LEVELS", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Confidence Scale" description="Flow confidence threshold multiplier"
          value={config.OMFG_OPTICAL_FLOW_CONFIDENCE_SCALE} min={1.0} max={10.0} step={0.5} showValue resetValue={4.0}
          onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_CONFIDENCE_SCALE", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="Motion Penalty" description="Regularisation penalty for large motions"
          value={config.OMFG_OPTICAL_FLOW_MOTION_PENALTY} min={0.0} max={0.1} step={0.001} showValue resetValue={0.01}
          onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_MOTION_PENALTY", v)} /></PanelSectionRow>
      </>)}

      {/* ── BFI ─────────────────────────────────────── */}
      {showBfi && (<>
        <SectionHeader title="Black Frame Insertion" />
        <PanelSectionRow><SliderField label="BFI Period" description="Insert a black frame every N real frames"
          value={config.OMFG_BFI_PERIOD} min={1} max={4} step={1} showValue
          onChange={(v) => onFieldChange("OMFG_BFI_PERIOD", v)} /></PanelSectionRow>
        <PanelSectionRow><SliderField label="BFI Hold (ms)" description="Duration to hold the black frame in ms"
          value={config.OMFG_BFI_HOLD_MS} min={1} max={33} step={1} showValue resetValue={8}
          onChange={(v) => onFieldChange("OMFG_BFI_HOLD_MS", v)} /></PanelSectionRow>
      </>)}

      {/* ── Visual hold (bfi / copy / history-copy) ─── */}
      {showVisual && (
        <PanelSectionRow><SliderField label="Visual Hold (ms)" description="Visual frame hold time in ms"
          value={config.OMFG_VISUAL_HOLD_MS} min={1} max={50} step={1} showValue resetValue={8}
          onChange={(v) => onFieldChange("OMFG_VISUAL_HOLD_MS", v)} /></PanelSectionRow>
      )}

      {/* ── Mode-specific flags ──────────────────────── */}
      {showBlend && (
        <PanelSectionRow>
          <ToggleField label="Present Original Frame First"
            description="For blend modes: present the real frame before the generated one"
            checked={config.OMFG_BLEND_ORIGINAL_PRESENT_FIRST === 1}
            onChange={(v) => onFieldChange("OMFG_BLEND_ORIGINAL_PRESENT_FIRST", v ? 1 : 0)} />
        </PanelSectionRow>
      )}
      {showCopy && (
        <PanelSectionRow>
          <ToggleField label="Present Original Frame First"
            description="For copy mode: present the real frame before the copy"
            checked={config.OMFG_COPY_ORIGINAL_PRESENT_FIRST === 1}
            onChange={(v) => onFieldChange("OMFG_COPY_ORIGINAL_PRESENT_FIRST", v ? 1 : 0)} />
        </PanelSectionRow>
      )}
      {showHistCopy && (
        <PanelSectionRow>
          <ToggleField label="Freeze History Frame"
            description="For history-copy: lock the history frame and stop updating it"
            checked={config.OMFG_HISTORY_COPY_FREEZE_HISTORY === 1}
            onChange={(v) => onFieldChange("OMFG_HISTORY_COPY_FREEZE_HISTORY", v ? 1 : 0)} />
        </PanelSectionRow>
      )}

      {/* ── Diagnostics ─────────────────────────────── */}
      <SectionHeader title="Diagnostics" />
      <PanelSectionRow>
        <ToggleField label="Present Timing" description="Log present/frame timing data to layer log"
          checked={config.OMFG_PRESENT_TIMING === 1}
          onChange={(v) => onFieldChange("OMFG_PRESENT_TIMING", v ? 1 : 0)} />
      </PanelSectionRow>
      <PanelSectionRow>
        <ToggleField label="Present Wait" description="Enable present-wait extension (reduces latency on supported hardware)"
          checked={config.OMFG_PRESENT_WAIT === 1}
          onChange={(v) => onFieldChange("OMFG_PRESENT_WAIT", v ? 1 : 0)} />
      </PanelSectionRow>
      {config.OMFG_PRESENT_WAIT === 1 && (
        <PanelSectionRow>
          <SliderField
            label={`Present Wait Timeout: ${Math.round(config.OMFG_PRESENT_WAIT_TIMEOUT_NS / 1e9)}s`}
            description="Timeout for present-wait in seconds (stored as nanoseconds)"
            value={config.OMFG_PRESENT_WAIT_TIMEOUT_NS}
            min={1_000_000_000} max={15_000_000_000} step={1_000_000_000}
            resetValue={5_000_000_000}
            onChange={(v) => onFieldChange("OMFG_PRESENT_WAIT_TIMEOUT_NS", v)} />
        </PanelSectionRow>
      )}
      <PanelSectionRow>
        <ToggleField label="Benchmark Mode" description="Emit benchmark metrics to layer log"
          checked={config.OMFG_BENCHMARK === 1}
          onChange={(v) => onFieldChange("OMFG_BENCHMARK", v ? 1 : 0)} />
      </PanelSectionRow>
      {config.OMFG_BENCHMARK === 1 && (
        <PanelSectionRow>
          <TextField label="Benchmark Label" description="Label used in benchmark log output"
            value={config.OMFG_BENCHMARK_LABEL}
            onChange={(e) => onFieldChange("OMFG_BENCHMARK_LABEL", e.target.value)} />
        </PanelSectionRow>
      )}

      {/* ── Startup-scoped ──────────────────────────── */}
      <SectionHeader title="Startup-scoped" sub="⚠ requires game restart" />
      <PanelSectionRow>
        <SliderField label="Swapchain Image Bump" description="Override swapchain image count bump (0 = auto)"
          value={config.OMFG_SWAPCHAIN_IMAGE_BUMP_OVERRIDE} min={0} max={4} step={1} showValue resetValue={0}
          onChange={(v) => onFieldChange("OMFG_SWAPCHAIN_IMAGE_BUMP_OVERRIDE", v)} />
      </PanelSectionRow>
      <PanelSectionRow>
        <ToggleField label="Device Debug" description="Enable Vulkan device debug validation layers"
          checked={config.OMFG_CREATE_DEVICE_DEBUG === 1}
          onChange={(v) => onFieldChange("OMFG_CREATE_DEVICE_DEBUG", v ? 1 : 0)} />
      </PanelSectionRow>
      <PanelSectionRow>
        <ToggleField label="Append Timing Extensions" description="Request present-timing Vulkan extensions on device creation"
          checked={config.OMFG_CREATE_DEVICE_APPEND_TIMING_EXTENSIONS === 1}
          onChange={(v) => onFieldChange("OMFG_CREATE_DEVICE_APPEND_TIMING_EXTENSIONS", v ? 1 : 0)} />
      </PanelSectionRow>
      <PanelSectionRow>
        <ToggleField label="Append Timing Features" description="Request present-timing Vulkan features on device creation"
          checked={config.OMFG_CREATE_DEVICE_APPEND_TIMING_FEATURES === 1}
          onChange={(v) => onFieldChange("OMFG_CREATE_DEVICE_APPEND_TIMING_FEATURES", v ? 1 : 0)} />
      </PanelSectionRow>

      {/* ── Reset ───────────────────────────────────── */}
      <SectionHeader title="Reset" />
      <PanelSectionRow>
        <ButtonItem layout="below"
          description="Restore all settings to factory defaults (current config backed up to .toml.bak)"
          onClick={onReset}>
          Reset to Defaults
        </ButtonItem>
      </PanelSectionRow>
        </>
      )}
    </>
  );
}
