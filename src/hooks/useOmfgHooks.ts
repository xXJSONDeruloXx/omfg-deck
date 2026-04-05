import { useState, useEffect, useCallback } from "react";
import { toaster } from "@decky/api";
import {
  checkOmfgInstalled,
  getOmfgConfig,
  saveConfig,
} from "../api/omfgApi";
import { OmfgConfig, getDefaults } from "../config/configSchema";

// ---------------------------------------------------------------------------
// Installation status hook
// ---------------------------------------------------------------------------

export function useInstallationStatus() {
  const [isInstalled, setIsInstalled] = useState(false);
  const [installationStatus, setInstallationStatus] = useState("");

  const checkInstallation = useCallback(async () => {
    try {
      const status = await checkOmfgInstalled();
      setIsInstalled(status.installed);
      setInstallationStatus(status.installed ? "OMFG layer installed" : "OMFG layer not installed");
      return status.installed;
    } catch {
      setInstallationStatus("OMFG layer not installed");
      return false;
    }
  }, []);

  useEffect(() => {
    checkInstallation();
  }, [checkInstallation]);

  return { isInstalled, installationStatus, setIsInstalled, setInstallationStatus, checkInstallation };
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

  useEffect(() => {
    loadConfig();
  }, []); // intentionally empty — run once on mount

  return { config, loadConfig, updateConfig, updateField };
}
