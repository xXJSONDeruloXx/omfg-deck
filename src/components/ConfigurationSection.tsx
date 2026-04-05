import React from "react";
import { PanelSectionRow, ToggleField, SliderField } from "@decky/ui";
import { OmfgConfig, ALL_LAYER_MODES, DEBUG_VIEWS, isMultiMode, isAdaptiveMode, isReprojectMode, isOptflowMode } from "../config/configSchema";

// A minimal dropdown/cycle control using a ButtonItem-style wrapper
function CycleField({
  label,
  description,
  value,
  options,
  onChange,
}: {
  label: string;
  description?: string;
  value: string;
  options: readonly string[];
  onChange: (v: string) => void;
}) {
  const idx = options.indexOf(value as any);
  const next = options[(idx + 1) % options.length];
  const prev = options[(idx - 1 + options.length) % options.length];

  return (
    <div style={{ marginBottom: "6px" }}>
      <div style={{ fontSize: "13px", fontWeight: "600", marginBottom: "2px" }}>{label}</div>
      {description && (
        <div style={{ fontSize: "11px", opacity: 0.7, marginBottom: "4px" }}>{description}</div>
      )}
      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
        <button
          style={btnStyle}
          onClick={() => onChange(prev)}
        >
          ◀
        </button>
        <div
          style={{
            flex: 1,
            textAlign: "center",
            fontSize: "12px",
            background: "rgba(255,255,255,0.08)",
            borderRadius: "4px",
            padding: "4px 6px",
            fontFamily: "monospace",
          }}
        >
          {value}
        </div>
        <button
          style={btnStyle}
          onClick={() => onChange(next)}
        >
          ▶
        </button>
      </div>
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  background: "rgba(255,255,255,0.12)",
  border: "none",
  borderRadius: "4px",
  color: "#fff",
  cursor: "pointer",
  padding: "4px 8px",
  fontSize: "13px",
};

function SectionHeader({ title }: { title: string }) {
  return (
    <PanelSectionRow>
      <div
        style={{
          fontSize: "13px",
          fontWeight: "bold",
          marginTop: "12px",
          marginBottom: "4px",
          borderBottom: "1px solid rgba(255,255,255,0.2)",
          paddingBottom: "4px",
          textTransform: "uppercase",
          letterSpacing: "0.05em",
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
}

export function ConfigurationSection({ config, onFieldChange }: ConfigurationSectionProps) {
  const mode = config.OMFG_LAYER_MODE;
  const showMulti = isMultiMode(mode);
  const showAdaptive = isAdaptiveMode(mode);
  const showReproject = isReprojectMode(mode);
  const showOptflow = isOptflowMode(mode);
  const showBfi = mode === "bfi";

  return (
    <>
      <SectionHeader title="Mode" />

      <PanelSectionRow>
        <CycleField
          label="Layer Mode"
          description="Frame generation algorithm"
          value={config.OMFG_LAYER_MODE}
          options={ALL_LAYER_MODES}
          onChange={(v) => onFieldChange("OMFG_LAYER_MODE", v)}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <CycleField
          label="Debug View"
          description="Overlay visualisation (off = normal)"
          value={config.OMFG_DEBUG_VIEW}
          options={DEBUG_VIEWS}
          onChange={(v) => onFieldChange("OMFG_DEBUG_VIEW", v)}
        />
      </PanelSectionRow>

      {/* Multi / adaptive settings */}
      {(showMulti || showAdaptive) && (
        <>
          <SectionHeader title="Multi / Adaptive" />

          {showMulti && (
            <PanelSectionRow>
              <SliderField
                label={`Generated Frames: ${config.OMFG_MULTI_BLEND_COUNT}`}
                description="Number of frames to generate between real frames"
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
                onChange={(v) => onFieldChange("OMFG_MULTI_BLEND_COUNT", v)}
              />
            </PanelSectionRow>
          )}

          {showAdaptive && (
            <>
              <PanelSectionRow>
                <SliderField
                  label={`Target FPS: ${config.OMFG_ADAPTIVE_MULTI_TARGET_FPS}`}
                  description="Adaptive controller target frame rate"
                  value={config.OMFG_ADAPTIVE_MULTI_TARGET_FPS}
                  min={30}
                  max={240}
                  step={5}
                  onChange={(v) => onFieldChange("OMFG_ADAPTIVE_MULTI_TARGET_FPS", v)}
                />
              </PanelSectionRow>
              <PanelSectionRow>
                <SliderField
                  label={`Min Generated: ${config.OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES}`}
                  description="Minimum generated frames per real frame"
                  value={config.OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES}
                  min={0}
                  max={3}
                  step={1}
                  onChange={(v) => onFieldChange("OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES", v)}
                />
              </PanelSectionRow>
              <PanelSectionRow>
                <SliderField
                  label={`Max Generated: ${config.OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES}`}
                  description="Maximum generated frames per real frame"
                  value={config.OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES}
                  min={1}
                  max={4}
                  step={1}
                  onChange={(v) => onFieldChange("OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES", v)}
                />
              </PanelSectionRow>
            </>
          )}
        </>
      )}

      {/* Reproject settings */}
      {showReproject && (
        <>
          <SectionHeader title="Reprojection" />

          <PanelSectionRow>
            <SliderField
              label={`Search Radius: ${config.OMFG_REPROJECT_SEARCH_RADIUS}`}
              description="Motion search radius (higher = more accurate, slower)"
              value={config.OMFG_REPROJECT_SEARCH_RADIUS}
              min={1}
              max={6}
              step={1}
              onChange={(v) => onFieldChange("OMFG_REPROJECT_SEARCH_RADIUS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label={`Patch Radius: ${config.OMFG_REPROJECT_PATCH_RADIUS}`}
              description="Comparison patch radius"
              value={config.OMFG_REPROJECT_PATCH_RADIUS}
              min={1}
              max={4}
              step={1}
              onChange={(v) => onFieldChange("OMFG_REPROJECT_PATCH_RADIUS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label={`Confidence Scale: ${config.OMFG_REPROJECT_CONFIDENCE_SCALE.toFixed(1)}`}
              description="Motion confidence threshold scale"
              value={config.OMFG_REPROJECT_CONFIDENCE_SCALE}
              min={1.0}
              max={10.0}
              step={0.5}
              onChange={(v) => onFieldChange("OMFG_REPROJECT_CONFIDENCE_SCALE", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label={`Disocclusion Bias: ${config.OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS.toFixed(2)}`}
              description="Bias towards current frame in disocclusion regions"
              value={config.OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS}
              min={0.0}
              max={1.0}
              step={0.05}
              onChange={(v) => onFieldChange("OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label={`Hole Fill Strength: ${config.OMFG_REPROJECT_HOLE_FILL_STRENGTH.toFixed(2)}`}
              description="Strength of hole fill in disoccluded areas"
              value={config.OMFG_REPROJECT_HOLE_FILL_STRENGTH}
              min={0.0}
              max={1.0}
              step={0.05}
              onChange={(v) => onFieldChange("OMFG_REPROJECT_HOLE_FILL_STRENGTH", v)}
            />
          </PanelSectionRow>
        </>
      )}

      {/* Optical flow settings */}
      {showOptflow && (
        <>
          <SectionHeader title="Optical Flow" />

          <PanelSectionRow>
            <SliderField
              label={`Search Radius: ${config.OMFG_OPTICAL_FLOW_SEARCH_RADIUS}`}
              description="Optical flow search radius"
              value={config.OMFG_OPTICAL_FLOW_SEARCH_RADIUS}
              min={1}
              max={6}
              step={1}
              onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_SEARCH_RADIUS", v)}
            />
          </PanelSectionRow>

          <PanelSectionRow>
            <SliderField
              label={`Pyramid Levels: ${config.OMFG_OPTICAL_FLOW_LEVELS}`}
              description="Number of pyramid levels for multi-scale flow"
              value={config.OMFG_OPTICAL_FLOW_LEVELS}
              min={1}
              max={5}
              step={1}
              onChange={(v) => onFieldChange("OMFG_OPTICAL_FLOW_LEVELS", v)}
            />
          </PanelSectionRow>
        </>
      )}

      {/* BFI */}
      {showBfi && (
        <>
          <SectionHeader title="Black Frame Insertion" />
          <PanelSectionRow>
            <SliderField
              label={`BFI Period: ${config.OMFG_BFI_PERIOD}`}
              description="Insert a black frame every N real frames"
              value={config.OMFG_BFI_PERIOD}
              min={1}
              max={4}
              step={1}
              onChange={(v) => onFieldChange("OMFG_BFI_PERIOD", v)}
            />
          </PanelSectionRow>
        </>
      )}

      {/* Diagnostics */}
      <SectionHeader title="Diagnostics" />

      <PanelSectionRow>
        <ToggleField
          label="Present Timing"
          description="Log present timing data"
          checked={config.OMFG_PRESENT_TIMING === 1}
          onChange={(v) => onFieldChange("OMFG_PRESENT_TIMING", v ? 1 : 0)}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ToggleField
          label="Benchmark Mode"
          description="Enable benchmarking output"
          checked={config.OMFG_BENCHMARK === 1}
          onChange={(v) => onFieldChange("OMFG_BENCHMARK", v ? 1 : 0)}
        />
      </PanelSectionRow>
    </>
  );
}
