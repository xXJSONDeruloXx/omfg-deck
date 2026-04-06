import { callable } from "@decky/api";
import { OmfgConfig } from "../config/configSchema";

export interface InstallationResult {
  success: boolean;
  message?: string;
  error?: string;
}

export interface InstallationStatus {
  installed: boolean;
  lib_exists: boolean;
  json_exists: boolean;
  config_exists: boolean;
  wrapper_exists: boolean;
  installed_version: string;
  lib_path: string;
  json_path: string;
  error?: string;
}

export interface ConfigResult {
  success: boolean;
  config?: OmfgConfig;
  message?: string;
  error?: string;
}

export interface SchemaResult {
  defaults: OmfgConfig;
  modes: string[];
  debug_views: string[];
}

export interface LaunchOptionResult {
  success: boolean;
  launch_option: string;
}

export interface LayerEnabledResult {
  success: boolean;
  enabled: boolean;
  error?: string;
}

export interface LayerLogResult {
  success: boolean;
  log: string;
  message?: string;
  error?: string;
}

export interface WorkaroundsResult {
  success: boolean;
  mesa_immediate: boolean;
  disable_vkbasalt: boolean;
  force_enable_vkbasalt: boolean;
  dxvk_frame_rate: number;
  enable_wow64: boolean;
  disable_steamdeck: boolean;
  mangohud: boolean;
  enable_gamescope_wsi: boolean;
  enable_zink: boolean;
  error?: string;
}

export interface SetWorkaroundResult {
  success: boolean;
  key?: string;
  value?: string;
  error?: string;
}

export interface FileContentResult {
  success: boolean;
  content: string;
  message?: string;
  error?: string;
}

export interface UpdateCheckResult {
  success: boolean;
  update_available: boolean;
  current_version: string;
  latest_version: string;
  release_notes: string;
  release_date: string;
  download_url: string;
  error?: string;
}

export interface UpdateDownloadResult {
  success: boolean;
  download_path?: string;
  error?: string;
}

// --- callable bindings ---

export const installOmfg       = callable<[], InstallationResult>("install_omfg");
export const uninstallOmfg     = callable<[], InstallationResult>("uninstall_omfg");
export const checkOmfgInstalled = callable<[], InstallationStatus>("check_omfg_installed");

export const getOmfgConfig    = callable<[], ConfigResult>("get_omfg_config");
export const updateOmfgConfig = callable<[config_json: string], ConfigResult>("update_omfg_config");
export const resetOmfgConfig  = callable<[], ConfigResult>("reset_omfg_config");

export const getConfigSchema  = callable<[], SchemaResult>("get_config_schema");
export const getLaunchOption  = callable<[], LaunchOptionResult>("get_launch_option");

export const getLayerEnabled  = callable<[], LayerEnabledResult>("get_layer_enabled");
export const setLayerEnabled  = callable<[enabled: boolean], LayerEnabledResult>("set_layer_enabled");
export const getLayerLog      = callable<[lines: number], LayerLogResult>("get_layer_log");

export const getWorkarounds   = callable<[], WorkaroundsResult>("get_workarounds");
export const setWorkaround    = callable<[key: string, value: string], SetWorkaroundResult>("set_workaround");

export const getConfigFileContent   = callable<[], FileContentResult>("get_config_file_content");
export const getWrapperScriptContent = callable<[], FileContentResult>("get_wrapper_script_content");
export const getWrapperLaunchOption  = callable<[], LaunchOptionResult>("get_wrapper_launch_option");

export const checkForPluginUpdate  = callable<[], UpdateCheckResult>("check_for_plugin_update");
export const downloadPluginUpdate  = callable<[download_url: string], UpdateDownloadResult>("download_plugin_update");

// --- helper ---
export async function saveConfig(config: OmfgConfig): Promise<ConfigResult> {
  return updateOmfgConfig(JSON.stringify(config));
}
