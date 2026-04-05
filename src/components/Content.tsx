import { useEffect } from "react";
import { PanelSection } from "@decky/ui";
import { useInstallationStatus } from "../hooks/useOmfgHooks";
import { useOmfgConfig } from "../hooks/useOmfgHooks";
import { useInstallationActions } from "../hooks/useInstallationActions";
import { StatusDisplay } from "./StatusDisplay";
import { InstallationButton } from "./InstallationButton";
import { ConfigurationSection } from "./ConfigurationSection";
import { UsageInstructions } from "./UsageInstructions";
import { PluginUpdateChecker } from "./PluginUpdateChecker";
import { GitHubButton } from "./GitHubButton";
import { OmfgConfig } from "../config/configSchema";

export function Content() {
  const {
    isInstalled,
    installationStatus,
    setIsInstalled,
    setInstallationStatus,
  } = useInstallationStatus();

  const { config, loadConfig, updateField } = useOmfgConfig();
  const { isInstalling, isUninstalling, handleInstall, handleUninstall } = useInstallationActions();

  // Reload config when layer becomes installed
  useEffect(() => {
    if (isInstalled) {
      loadConfig();
    }
  }, [isInstalled, loadConfig]);

  const onInstall = () =>
    handleInstall(setIsInstalled, setInstallationStatus, loadConfig);

  const onUninstall = () =>
    handleUninstall(setIsInstalled, setInstallationStatus);

  const handleFieldChange = async (
    key: keyof OmfgConfig,
    value: OmfgConfig[keyof OmfgConfig]
  ) => {
    await updateField(key, value);
  };

  return (
    <PanelSection>
      <InstallationButton
        isInstalled={isInstalled}
        isInstalling={isInstalling}
        isUninstalling={isUninstalling}
        onInstall={onInstall}
        onUninstall={onUninstall}
      />

      <StatusDisplay
        isInstalled={isInstalled}
        installationStatus={installationStatus}
      />

      {isInstalled && (
        <ConfigurationSection
          config={config}
          onFieldChange={handleFieldChange}
        />
      )}

      <UsageInstructions config={config} />

      <GitHubButton />

      <PluginUpdateChecker />
    </PanelSection>
  );
}
