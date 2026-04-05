/**
 * Centralized configuration schema for omfg-deck.
 * Keys match the OMFG_* environment variable names used in omfg-live.toml [env].
 */

export const LAYER_MODES_UTILITY = [
  "passthrough", "clear", "bfi", "copy", "history-copy",
] as const;

export const LAYER_MODES_SINGLE = [
  "blend", "adaptive-blend", "search-blend", "search-adaptive-blend",
  "reproject-blend", "reproject-adaptive-blend", "optflow-blend",
] as const;

export const LAYER_MODES_MULTI = [
  "multi-blend", "adaptive-multi-blend", "reproject-multi-blend",
  "reproject-adaptive-multi-blend", "optflow-multi-blend", "optflow-adaptive-multi-blend",
] as const;

export const ALL_LAYER_MODES = [
  ...LAYER_MODES_UTILITY,
  ...LAYER_MODES_SINGLE,
  ...LAYER_MODES_MULTI,
] as const;

export type LayerMode = (typeof ALL_LAYER_MODES)[number];

export const DEBUG_VIEWS = [
  "off", "motion", "confidence", "ambiguity", "disocclusion", "hole-fill", "fallback",
] as const;
export type DebugView = (typeof DEBUG_VIEWS)[number];

// ---------------------------------------------------------------------------
// Typed config object
// ---------------------------------------------------------------------------

export interface OmfgConfig {
  OMFG_LAYER_MODE: string;
  OMFG_DEBUG_VIEW: string;
  // Reproject
  OMFG_REPROJECT_SEARCH_RADIUS: number;
  OMFG_REPROJECT_PATCH_RADIUS: number;
  OMFG_REPROJECT_CONFIDENCE_SCALE: number;
  OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS: number;
  OMFG_REPROJECT_DISOCCLUSION_SCALE: number;
  OMFG_REPROJECT_HOLE_FILL_STRENGTH: number;
  OMFG_REPROJECT_HOLE_FILL_RADIUS: number;
  OMFG_REPROJECT_GRADIENT_CONFIDENCE_WEIGHT: number;
  OMFG_REPROJECT_CHROMA_WEIGHT: number;
  OMFG_REPROJECT_AMBIGUITY_SCALE: number;
  // Optical flow
  OMFG_OPTICAL_FLOW_SEARCH_RADIUS: number;
  OMFG_OPTICAL_FLOW_PATCH_RADIUS: number;
  OMFG_OPTICAL_FLOW_LEVELS: number;
  OMFG_OPTICAL_FLOW_CONFIDENCE_SCALE: number;
  OMFG_OPTICAL_FLOW_MOTION_PENALTY: number;
  // Multi / adaptive
  OMFG_MULTI_BLEND_COUNT: number;
  OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES: number;
  OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES: number;
  OMFG_ADAPTIVE_MULTI_TARGET_FPS: number;
  OMFG_ADAPTIVE_MULTI_INTERVAL_THRESHOLD_MS: number;
  // BFI / visual timing
  OMFG_BFI_PERIOD: number;
  OMFG_BFI_HOLD_MS: number;
  OMFG_VISUAL_HOLD_MS: number;
  // Mode-specific flags
  OMFG_BLEND_ORIGINAL_PRESENT_FIRST: number;
  OMFG_COPY_ORIGINAL_PRESENT_FIRST: number;
  OMFG_HISTORY_COPY_FREEZE_HISTORY: number;
  // Diagnostics
  OMFG_PRESENT_TIMING: number;
  OMFG_PRESENT_WAIT: number;
  OMFG_PRESENT_WAIT_TIMEOUT_NS: number;
  OMFG_BENCHMARK: number;
  OMFG_BENCHMARK_LABEL: string;
  // Startup-scoped (need game restart)
  OMFG_SWAPCHAIN_IMAGE_BUMP_OVERRIDE: number;
  OMFG_CREATE_DEVICE_DEBUG: number;
  OMFG_CREATE_DEVICE_APPEND_TIMING_EXTENSIONS: number;
  OMFG_CREATE_DEVICE_APPEND_TIMING_FEATURES: number;
}

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

export const DEFAULT_CONFIG: OmfgConfig = {
  OMFG_LAYER_MODE: "reproject-blend",
  OMFG_DEBUG_VIEW: "off",
  OMFG_REPROJECT_SEARCH_RADIUS: 2,
  OMFG_REPROJECT_PATCH_RADIUS: 1,
  OMFG_REPROJECT_CONFIDENCE_SCALE: 4.0,
  OMFG_REPROJECT_DISOCCLUSION_CURRENT_BIAS: 0.75,
  OMFG_REPROJECT_DISOCCLUSION_SCALE: 2.0,
  OMFG_REPROJECT_HOLE_FILL_STRENGTH: 0.85,
  OMFG_REPROJECT_HOLE_FILL_RADIUS: 2,
  OMFG_REPROJECT_GRADIENT_CONFIDENCE_WEIGHT: 8.0,
  OMFG_REPROJECT_CHROMA_WEIGHT: 0.3,
  OMFG_REPROJECT_AMBIGUITY_SCALE: 6.0,
  OMFG_OPTICAL_FLOW_SEARCH_RADIUS: 2,
  OMFG_OPTICAL_FLOW_PATCH_RADIUS: 1,
  OMFG_OPTICAL_FLOW_LEVELS: 3,
  OMFG_OPTICAL_FLOW_CONFIDENCE_SCALE: 4.0,
  OMFG_OPTICAL_FLOW_MOTION_PENALTY: 0.01,
  OMFG_MULTI_BLEND_COUNT: 2,
  OMFG_ADAPTIVE_MULTI_MIN_GENERATED_FRAMES: 0,
  OMFG_ADAPTIVE_MULTI_MAX_GENERATED_FRAMES: 2,
  OMFG_ADAPTIVE_MULTI_TARGET_FPS: 120,
  OMFG_ADAPTIVE_MULTI_INTERVAL_THRESHOLD_MS: 1.0,
  OMFG_BFI_PERIOD: 1,
  OMFG_BFI_HOLD_MS: 8,
  OMFG_VISUAL_HOLD_MS: 8,
  OMFG_BLEND_ORIGINAL_PRESENT_FIRST: 0,
  OMFG_COPY_ORIGINAL_PRESENT_FIRST: 0,
  OMFG_HISTORY_COPY_FREEZE_HISTORY: 0,
  OMFG_PRESENT_TIMING: 0,
  OMFG_PRESENT_WAIT: 0,
  OMFG_PRESENT_WAIT_TIMEOUT_NS: 5_000_000_000,
  OMFG_BENCHMARK: 0,
  OMFG_BENCHMARK_LABEL: "live",
  OMFG_SWAPCHAIN_IMAGE_BUMP_OVERRIDE: 0,
  OMFG_CREATE_DEVICE_DEBUG: 0,
  OMFG_CREATE_DEVICE_APPEND_TIMING_EXTENSIONS: 0,
  OMFG_CREATE_DEVICE_APPEND_TIMING_FEATURES: 0,
};

export function getDefaults(): OmfgConfig {
  return { ...DEFAULT_CONFIG };
}

// ---------------------------------------------------------------------------
// Mode classification helpers
// ---------------------------------------------------------------------------

export function isMultiMode(mode: string): boolean {
  return (LAYER_MODES_MULTI as readonly string[]).includes(mode);
}
export function isOptflowMode(mode: string): boolean {
  return mode.startsWith("optflow");
}
export function isReprojectMode(mode: string): boolean {
  return mode.startsWith("reproject") || mode.startsWith("search");
}
export function isAdaptiveMode(mode: string): boolean {
  return mode.includes("adaptive");
}
export function isBfiMode(mode: string): boolean {
  return mode === "bfi";
}
export function isBlendMode(mode: string): boolean {
  return mode.includes("blend");
}
export function isCopyMode(mode: string): boolean {
  return mode === "copy";
}
export function isHistoryCopyMode(mode: string): boolean {
  return mode === "history-copy";
}
export function isVisualMode(mode: string): boolean {
  // modes that use OMFG_VISUAL_HOLD_MS
  return mode === "bfi" || mode === "copy" || mode === "history-copy";
}
