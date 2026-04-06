import { useEffect } from "react";
import { PanelSection, PanelSectionRow, ToggleField, ButtonItem, showModal } from "@decky/ui";
import { FaTools } from "react-icons/fa";
import { useInstallationStatus, useOmfgConfig, useLayerEnabled } from "../hooks/useOmfgHooks";
import { useInstallationActions } from "../hooks/useInstallationActions";
import { useWorkarounds } from "../hooks/useWorkarounds";
import { StatusDisplay } from "./StatusDisplay";
import { InstallationButton } from "./InstallationButton";
import { ConfigurationSection } from "./ConfigurationSection";
import { WorkaroundsSection } from "./WorkaroundsSection";
import { UsageInstructions } from "./UsageInstructions";
import { PluginUpdateChecker } from "./PluginUpdateChecker";
import { GitHubButton } from "./GitHubButton";
import { LogViewer } from "./LogViewer";
import { NerdStuffModal } from "./NerdStuffModal";
import { OmfgConfig } from "../config/configSchema";
import { WorkaroundState } from "../hooks/useWorkarounds";

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
  const { layerEnabled, toggleEnabled } = useLayerEnabled();
  const { workarounds, toggle: toggleWorkaround, setInt: setWorkaroundInt } = useWorkarounds();
  const { isInstalling, isUninstalling, handleInstall, handleUninstall } = useInstallationActions();

  useEffect(() => {
    if (isInstalled) loadConfig();
  }, [isInstalled, loadConfig]);

  const onInstall = () =>
    handleInstall(setIsInstalled, setInstallationStatus, async () => {
      await loadConfig();
      await checkInstallation();
    });
  const onUninstall = () => handleUninstall(setIsInstalled, setInstallationStatus);

  const handleFieldChange = async (key: keyof OmfgConfig, value: OmfgConfig[keyof OmfgConfig]) => {
    await updateField(key, value);
  };

  const handleWorkaroundToggle = async (key: keyof WorkaroundState, enabled: boolean) =>
    toggleWorkaround(key, enabled);

  const handleWorkaroundInt = async (key: keyof WorkaroundState, value: number) =>
    setWorkaroundInt(key, value);

  return (
    <PanelSection>
      {/* Global enable/disable */}
      <PanelSectionRow>
        <ToggleField
          label="OMFG Enabled"
          description={layerEnabled
            ? "Layer activates on games using the wrapper/launch option"
            : "Layer is globally disabled — games run without OMFG"}
          checked={layerEnabled}
          onChange={toggleEnabled}
        />
      </PanelSectionRow>

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

      <WorkaroundsSection
        workarounds={workarounds}
        onToggle={handleWorkaroundToggle}
        onSetInt={handleWorkaroundInt}
      />

      <UsageInstructions config={config} />

      {isInstalled && <LogViewer />}

      {/* Nerd Stuff */}
      {isInstalled && (
        <PanelSectionRow>
          <ButtonItem layout="below" onClick={() => showModal(<NerdStuffModal />)}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <FaTools />
              <div>Nerd Stuff</div>
            </div>
          </ButtonItem>
        </PanelSectionRow>
      )}

      <GitHubButton />

      <PluginUpdateChecker />
    </PanelSection>
  );
}
