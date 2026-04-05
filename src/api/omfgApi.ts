import { callable } from "@decky/api";
import { OmfgConfig } from "../config/configSchema";

// --- shared response shapes ---

export interface InstallationResult {
  success: boolean;
  message?: string;
  error?: string;
}

export interface InstallationStatus {
  installed: boolean;
  lib_exists: boolean;
  json_exists: boolean;
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

export const installOmfg = callable<[], InstallationResult>("install_omfg");
export const uninstallOmfg = callable<[], InstallationResult>("uninstall_omfg");
export const checkOmfgInstalled = callable<[], InstallationStatus>("check_omfg_installed");

export const getOmfgConfig = callable<[], ConfigResult>("get_omfg_config");
/** config is passed as a JSON string to avoid positional-arg explosion */
export const updateOmfgConfig = callable<[config_json: string], ConfigResult>("update_omfg_config");

export const getConfigSchema = callable<[], SchemaResult>("get_config_schema");
export const getLaunchOption = callable<[], LaunchOptionResult>("get_launch_option");

export const checkForPluginUpdate = callable<[], UpdateCheckResult>("check_for_plugin_update");
export const downloadPluginUpdate = callable<[download_url: string], UpdateDownloadResult>("download_plugin_update");

// --- helper: send a full OmfgConfig object ---
export async function saveConfig(config: OmfgConfig): Promise<ConfigResult> {
  return updateOmfgConfig(JSON.stringify(config));
}
