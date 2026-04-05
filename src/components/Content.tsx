import { useEffect } from "react";
import { PanelSection } from "@decky/ui";
import { useInstallationStatus, useOmfgConfig } from "../hooks/useOmfgHooks";
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
    configExists,
    wrapperExists,
    setIsInstalled,
    setInstallationStatus,
    checkInstallation,
  } = useInstallationStatus();

  const { config, loadConfig, updateField, resetConfig } = useOmfgConfig();
  const { isInstalling, isUninstalling, handleInstall, handleUninstall } = useInstallationActions();

  // Re-check full status after install/uninstall
  useEffect(() => {
    if (isInstalled) {
      loadConfig();
    }
  }, [isInstalled, loadConfig]);

  const onInstall = () =>
    handleInstall(setIsInstalled, setInstallationStatus, async () => {
      await loadConfig();
      await checkInstallation();
    });

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
        configExists={configExists}
        wrapperExists={wrapperExists}
      />

      {isInstalled && (
        <ConfigurationSection
          config={config}
          onFieldChange={handleFieldChange}
          onReset={resetConfig}
        />
      )}

      <UsageInstructions config={config} />

      <GitHubButton />

      <PluginUpdateChecker />
    </PanelSection>
  );
}
