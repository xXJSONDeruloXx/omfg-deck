import { useState } from "react";
import { toaster } from "@decky/api";
import { installOmfg, uninstallOmfg } from "../api/omfgApi";

export function useInstallationActions() {
  const [isInstalling, setIsInstalling] = useState(false);
  const [isUninstalling, setIsUninstalling] = useState(false);

  const handleInstall = async (
    setIsInstalled: (v: boolean) => void,
    setInstallationStatus: (s: string) => void,
    reloadConfig?: () => Promise<void>
  ) => {
    setIsInstalling(true);
    setInstallationStatus("Downloading and installing OMFG layer...");
    try {
      const result = await installOmfg();
      if (result.success) {
        setIsInstalled(true);
        setInstallationStatus("OMFG layer installed!");
        toaster.toast({ title: "Installation Complete", body: "OMFG layer installed successfully" });
        if (reloadConfig) await reloadConfig();
      } else {
        setInstallationStatus(`Installation failed: ${result.error}`);
        toaster.toast({ title: "Installation Failed", body: result.error ?? "Unknown error" });
      }
    } catch (e) {
      setInstallationStatus(`Installation failed: ${e}`);
      toaster.toast({ title: "Installation Failed", body: String(e) });
    } finally {
      setIsInstalling(false);
    }
  };

  const handleUninstall = async (
    setIsInstalled: (v: boolean) => void,
    setInstallationStatus: (s: string) => void
  ) => {
    setIsUninstalling(true);
    setInstallationStatus("Uninstalling OMFG layer...");
    try {
      const result = await uninstallOmfg();
      if (result.success) {
        setIsInstalled(false);
        setInstallationStatus("OMFG layer uninstalled");
        toaster.toast({ title: "Uninstalled", body: result.message ?? "OMFG layer removed" });
      } else {
        setInstallationStatus(`Uninstall failed: ${result.error}`);
        toaster.toast({ title: "Uninstall Failed", body: result.error ?? "Unknown error" });
      }
    } catch (e) {
      setInstallationStatus(`Uninstall failed: ${e}`);
      toaster.toast({ title: "Uninstall Failed", body: String(e) });
    } finally {
      setIsUninstalling(false);
    }
  };

  return { isInstalling, isUninstalling, handleInstall, handleUninstall };
}
