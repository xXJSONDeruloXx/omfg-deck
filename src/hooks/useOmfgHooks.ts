import { useState, useEffect, useCallback } from "react";
import { toaster } from "@decky/api";
import {
  checkOmfgInstalled,
  getOmfgConfig,
  saveConfig,
  resetOmfgConfig,
  getLayerEnabled,
  setLayerEnabled,
} from "../api/omfgApi";
import { OmfgConfig, getDefaults } from "../config/configSchema";

// ---------------------------------------------------------------------------
// Installation status hook
// ---------------------------------------------------------------------------

export function useInstallationStatus() {
  const [isInstalled, setIsInstalled] = useState(false);
  const [installationStatus, setInstallationStatus] = useState("");
  const [configExists, setConfigExists] = useState(false);
  const [wrapperExists, setWrapperExists] = useState(false);
  const [installedVersion, setInstalledVersion] = useState("");

  const checkInstallation = useCallback(async () => {
    try {
      const status = await checkOmfgInstalled();
      setIsInstalled(status.installed);
      setConfigExists(status.config_exists ?? false);
      setWrapperExists(status.wrapper_exists ?? false);
      setInstalledVersion(status.installed_version ?? "");
      setInstallationStatus(
        status.installed
          ? status.installed_version
            ? `OMFG layer installed (v${status.installed_version})`
            : "OMFG layer installed"
          : "OMFG layer not installed"
      );
      return status.installed;
    } catch {
      setInstallationStatus("OMFG layer not installed");
      return false;
    }
  }, []);

  useEffect(() => {
    checkInstallation();
  }, [checkInstallation]);

  return {
    isInstalled,
    installationStatus,
    configExists,
    wrapperExists,
    installedVersion,
    setIsInstalled,
    setInstallationStatus,
    checkInstallation,
  };
}

// ---------------------------------------------------------------------------
// Config hook
// ---------------------------------------------------------------------------

export function useOmfgConfig() {
  const [config, setConfig] = useState<OmfgConfig>(() => getDefaults());

  const loadConfig = useCallback(async () => {
    try {
      const result = await getOmfgConfig();
      if (result.success && result.config) {
        setConfig(result.config);
      }
    } catch (e) {
      console.error("Error loading omfg config:", e);
    }
  }, []);

  const updateConfig = useCallback(async (next: OmfgConfig) => {
    try {
      const result = await saveConfig(next);
      if (result.success) {
        setConfig(next);
      } else {
        toaster.toast({ title: "Config update failed", body: result.error ?? "Unknown error" });
      }
      return result;
    } catch (e) {
      toaster.toast({ title: "Config update failed", body: String(e) });
      return { success: false, error: String(e) };
    }
  }, []);

  const updateField = useCallback(
    async (key: keyof OmfgConfig, value: OmfgConfig[keyof OmfgConfig]) => {
      const next = { ...config, [key]: value };
      return updateConfig(next);
    },
    [config, updateConfig]
  );

  const resetConfig = useCallback(async () => {
    try {
      const result = await resetOmfgConfig();
      if (result.success && result.config) {
        setConfig(result.config as OmfgConfig);
        toaster.toast({ title: "Config Reset", body: "Settings restored to defaults" });
      } else {
        toaster.toast({ title: "Reset failed", body: result.error ?? "Unknown error" });
      }
      return result;
    } catch (e) {
      toaster.toast({ title: "Reset failed", body: String(e) });
      return { success: false, error: String(e) };
    }
  }, []);

  useEffect(() => {
    loadConfig();
  }, []); // intentionally empty — run once on mount

  return { config, loadConfig, updateConfig, updateField, resetConfig };
}

// ---------------------------------------------------------------------------
// Global layer enable/disable hook
// ---------------------------------------------------------------------------

export function useLayerEnabled() {
  const [layerEnabled, setLayerEnabledState] = useState(true);

  const fetchEnabled = useCallback(async () => {
    try {
      const result = await getLayerEnabled();
      if (result.success) setLayerEnabledState(result.enabled);
    } catch { /* keep default true */ }
  }, []);

  const toggleEnabled = useCallback(async (enabled: boolean) => {
    try {
      const result = await setLayerEnabled(enabled);
      if (result.success) {
        setLayerEnabledState(enabled);
        toaster.toast({
          title: enabled ? "Layer Enabled" : "Layer Disabled",
          body: enabled
            ? "OMFG will activate on next game launch"
            : "OMFG is globally disabled — wrapper script will skip layer",
        });
      } else {
        toaster.toast({ title: "Failed", body: result.error ?? "Unknown error" });
      }
    } catch (e) {
      toaster.toast({ title: "Failed", body: String(e) });
    }
  }, []);

  useEffect(() => { fetchEnabled(); }, [fetchEnabled]);

  return { layerEnabled, toggleEnabled };
}
