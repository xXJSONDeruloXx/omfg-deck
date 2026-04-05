import { PanelSectionRow, ToggleField, SliderField, DropdownItem, ButtonItem } from "@decky/ui";
import {
  OmfgConfig,
  ALL_LAYER_MODES,
  DEBUG_VIEWS,
  isMultiMode,
  isAdaptiveMode,
  isReprojectMode,
  isOptflowMode,
} from "../config/configSchema";

// Flat selectable options for DropdownItem
const MODE_OPTIONS_FLAT = ALL_LAYER_MODES.map((m) => ({ data: m, label: m }));
const DEBUG_OPTIONS = DEBUG_VIEWS.map((v) => ({ data: v, label: v }));

function SectionHeader({ title }: { title: string }) {
  return (
    <PanelSectionRow>
      <div
        style={{
          fontSize: "12px",
          fontWeight: "bold",
          marginTop: "10px",
          marginBottom: "2px",
          borderBottom: "1px solid rgba(255,255,255,0.18)",
          paddingBottom: "3px",
          textTransform: "uppercase",
          letterSpacing: "0.06em",
          opacity: 0.85,
        }}
      >
        {title}
      </div>
    </PanelSectionRow>
  );
}

interface ConfigurationSectionProps {
  config: OmfgConfig;
  onFieldChange: (key: keyof OmfgConfig, value: OmfgConfig[keyof OmfgConfig]) => Promise<void>;
  onReset: () => Promise<unknown>;
}

export function ConfigurationSection({ config, onFieldChange, onReset }: ConfigurationSectionProps) {
  const mode = config.OMFG_LAYER_MODE;
  const showMulti = isMultiMode(mode);
  const showAdaptive = isAdaptiveMode(mode);
  const showReproject = isReprojectMode(mode);
  const showOptflow = isOptflowMode(mode);
  const showBfi = mode === "bfi";

  return (
    <>
      {/* ── Mode ────────────────────────────────────── */}
      <SectionHeader title="Mode" />

      <PanelSectionRow>
        <DropdownItem
          label="Layer Mode"
          description="Frame generation algorithm family"
          rgOptions={MODE_OPTIONS_FLAT}
          selectedOption={config.OMFG_LAYER_MODE}
          onChange={(opt) => onFieldChange("OMFG_LAYER_MODE", opt.data)}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <DropdownItem
          label="Debug View"
          description="In-game diagnostic overlay (off = normal)"
          rgOptions={DEBUG_OPTIONS}
          selectedOption={config.OMFG_DEBUG_VIEW}
          onChange={(opt) => onFieldChange("OMFG_DEBUG_VIEW", opt.data)}
        />
      </PanelSectionRow>

      {/* ── Multi / Adaptive ────────────────────────── */}
      {(showMulti || showAdaptive) && (
        <>
          <SectionHeader title="Multi / Adaptive" />

          {showMulti && (
            <PanelSectionRow>
              <SliderField
                label="Generated Frames"
                description="Frames to insert between each real frame"
                value={config.OMFG_MULTI_BLEND_COUNT}
                min={1}
                max={4}
                step={1}
                notchCount={4}
                notchLabels={[
                  { notchIndex: 0, label: "1" },
                  { notchIndex: 1, label: "2" },
                  { notchIndex: 2, label: "3" },
                  { notchIndex: 3, label: "4" },
                ]}
                showValue
                onChange={(v) => onFieldChange("OMFG_MULTI_BLEND_COUNT", v)}
              />
            </PanelSectionRow>
          )}

          {showAdaptive && (
            <>
              <PanelSectionRow>
                <SliderField
                  label="Target FPS"
                  description="Adaptive controller target frame rate"
                  value={config.OMFG_ADAPTIVE_MULTI_TARGET_FPS}
                  min={30}
                  max={240}
                  step={5}
                  showValue
                  onChange={(v) => onFieldChange("OMFG_ADAPTIVE_MULTI_TARGET_FPS", v)}
                />
              </PanelSectionRow>
              <PanelSectionRow>
                <SliderField
                  label="Min Generated Frames"
                  description="Minimum generated frames when adapting"
                  value={config.OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES}
                  min={0}
                  max={3}
                  step={1}
                  showValue
                  onChange={(v) => onFieldChange("OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES", v)}
                />
              </PanelSectionRow>
              <PanelSectionRow>
                <SliderField
                  label="Max Generated Frames"
                  description="Maximum generated frames when adapting"
                  value={config.OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES}
                  min={1}
                  max={4}
                  step={1}
                  showValue
                  onChange={(v) => onFieldChange("OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES", v)}
                />
              </PanelSectionRow>
            </>
          )}
        </>
      )}

      {/* ── Reprojection ────────────────────────────── */}
      {showReproject && (
        <>
          <SectionHeader title="Reprojection" />

          <PanelSectionRow>
            <SliderField
              label="Search Radius"
              description="Motion search radius (higher = more accurate, slower)"
              value={config.OMFG_REPROJECT_SEARCH_RADIUS}
              min={1}
              max={6}
              step={1}
              resetValue={2}
              showValue
              onChange={(v) => onFieldChange("OMFG_REPROJECT_SEARCH_RADIUS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Patch Radius"
              description="Comparison patch half-size"
              value={config.OMFG_REPROJECT_PATCH_RADIUS}
              min={1}
              max={4}
              step={1}
              resetValue={1}
              showValue
              onChange={(v) => onFieldChange("OMFG_REPROJECT_PATCH_RADIUS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Confidence Scale"
              description="Motion confidence threshold multiplier"
              value={config.OMFG_REPROJECT_CONFIDENCE_SCALE}
              min={1.0}
              max={10.0}
              step={0.5}
              resetValue={4.0}
              showValue
              onChange={(v) => onFieldChange("OMFG_REPROJECT_CONFIDENCE_SCALE", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Disocclusion Current Bias"
              description="Blend bias toward current frame in disoccluded regions"
              value={config.OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS}
              min={0.0}
              max={1.0}
              step={0.05}
              resetValue={0.75}
              showValue
              onChange={(v) => onFieldChange("OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Disocclusion Scale"
              description="Disocclusion region detection sensitivity"
              value={config.OMFG_REPROJECT_DISOCCLUSION_SCALE}
              min={0.5}
              max={6.0}
              step={0.25}
              resetValue={2.0}
              showValue
              onChange={(v) => onFieldChange("OMFG_REPROJECT_DISOCCLUSION_SCALE", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Hole Fill Strength"
              description="Strength of hole-filling in disoccluded areas"
              value={config.OMFG_REPROJECT_HOLE_FILL_STRENGTH}
              min={0.0}
              max={1.0}
              step={0.05}
              resetValue={0.85}
              showValue
              onChange={(v) => onFieldChange("OMFG_REPROJECT_HOLE_FILL_STRENGTH", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Hole Fill Radius"
              description="Spatial radius for hole-fill sampling"
              value={config.OMFG_REPROJECT_HOLE_FILL_RADIUS}
              min={1}
              max={6}
              step={1}
              resetValue={2}
              showValue
              onChange={(v) => onFieldChange("OMFG_REPROJECT_HOLE_FILL_RADIUS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Gradient Confidence Weight"
              description="Edge-gradient contribution to confidence score"
              value={config.OMFG_REPROJECT_GRADIENT_CONFIDENCE_WEIGHT}
              min={0.0}
              max={16.0}
              step={0.5}
              resetValue={8.0}
              showValue
              onChange={(v) => onFieldChange("OMFG_REPROJECT_GRADIENT_CONFIDENCE_WEIGHT", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Chroma Weight"
              description="Color/chroma contribution to motion matching"
              value={config.OMFG_REPROJECT_CHROMA_WEIGHT}
              min={0.0}
              max={1.0}
              step={0.05}
              resetValue={0.3}
              showValue
              onChange={(v) => onFieldChange("OMFG_REPROJECT_CHROMA_WEIGHT", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Ambiguity Scale"
              description="Multi-candidate motion ambiguity sensitivity"
              value={config.OMFG_REPROJECT_AMBIGUITY_SCALE}
              min={1.0}
              max={12.0}
              step={0.5}
              resetValue={6.0}
              showValue
              onChange={(v) => onFieldChange("OMFG_REPROJECT_AMBIGUITY_SCALE", v)}
            />
          </PanelSectionRow>
        </>
      )}

      {/* ── Optical Flow ────────────────────────────── */}
      {showOptflow && (
        <>
          <SectionHeader title="Optical Flow" />

          <PanelSectionRow>
            <SliderField
              label="Search Radius"
              description="Optical flow search radius"
              value={config.OMFG_OPTICAL_FLOW_SEARCH_RADIUS}
              min={1}
              max={6}
              step={1}
              resetValue={2}
              showValue
              onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_SEARCH_RADIUS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Patch Radius"
              description="Patch comparison half-size"
              value={config.OMFG_OPTICAL_FLOW_PATCH_RADIUS}
              min={1}
              max={4}
              step={1}
              resetValue={1}
              showValue
              onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_PATCH_RADIUS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Pyramid Levels"
              description="Multi-scale pyramid depth"
              value={config.OMFG_OPTICAL_FLOW_LEVELS}
              min={1}
              max={5}
              step={1}
              resetValue={3}
              showValue
              onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_LEVELS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Confidence Scale"
              description="Flow confidence threshold multiplier"
              value={config.OMFG_OPTICAL_FLOW_CONFIDENCE_SCALE}
              min={1.0}
              max={10.0}
              step={0.5}
              resetValue={4.0}
              showValue
              onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_CONFIDENCE_SCALE", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label="Motion Penalty"
              description="Regularisation penalty for large motions"
              value={config.OMFG_OPTICAL_FLOW_MOTION_PENALTY}
              min={0.0}
              max={0.1}
              step={0.001}
              resetValue={0.01}
              showValue
              onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_MOTION_PENALTY", v)}
            />
          </PanelSectionRow>
        </>
      )}

      {/* ── BFI ─────────────────────────────────────── */}
      {showBfi && (
        <>
          <SectionHeader title="Black Frame Insertion" />
          <PanelSectionRow>
            <SliderField
              label="BFI Period"
              description="Insert a black frame every N real frames"
              value={config.OMFG_BFI_PERIOD}
              min={1}
              max={4}
              step={1}
              showValue
              onChange={(v) => onFieldChange("OMFG_BFI_PERIOD", v)}
            />
          </PanelSectionRow>
        </>
      )}

      {/* ── Diagnostics ─────────────────────────────── */}
      <SectionHeader title="Diagnostics" />

      <PanelSectionRow>
        <ToggleField
          label="Present Timing"
          description="Log present/frame timing data to layer log"
          checked={config.OMFG_PRESENT_TIMING === 1}
          onChange={(v) => onFieldChange("OMFG_PRESENT_TIMING", v ? 1 : 0)}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Present Wait"
          description="Enable present-wait extension (reduces latency on supported hardware)"
          checked={config.OMFG_PRESENT_WAIT === 1}
          onChange={(v) => onFieldChange("OMFG_PRESENT_WAIT", v ? 1 : 0)}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Benchmark Mode"
          description="Emit benchmark metrics to layer log"
          checked={config.OMFG_BENCHMARK === 1}
          onChange={(v) => onFieldChange("OMFG_BENCHMARK", v ? 1 : 0)}
        />
      </PanelSectionRow>

      {/* ── Reset ───────────────────────────────────── */}
      <SectionHeader title="Reset" />

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          description="Restore all settings to factory defaults (current config backed up)"
          onClick={onReset}
        >
          Reset to Defaults
        </ButtonItem>
      </PanelSectionRow>
    </>
  );
}
