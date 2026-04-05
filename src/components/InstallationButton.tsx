import { ButtonItem, PanelSectionRow } from "@decky/ui";
import { FaDownload, FaTrash } from "react-icons/fa";

interface InstallationButtonProps {
  isInstalled: boolean;
  isInstalling: boolean;
  isUninstalling: boolean;
  onInstall: () => void;
  onUninstall: () => void;
}

export function InstallationButton({
  isInstalled,
  isInstalling,
  isUninstalling,
  onInstall,
  onUninstall,
}: InstallationButtonProps) {
  const label = isInstalling
    ? "Downloading & installing..."
    : isUninstalling
    ? "Uninstalling..."
    : isInstalled
    ? "Uninstall OMFG"
    : "Install OMFG";

  const icon = isInstalled && !isInstalling && !isUninstalling ? <FaTrash /> : <FaDownload />;

  return (
    <PanelSectionRow>
      <ButtonItem
        layout="below"
        onClick={isInstalled ? onUninstall : onInstall}
        disabled={isInstalling || isUninstalling}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {icon}
          <div>{label}</div>
        </div>
      </ButtonItem>
    </PanelSectionRow>
  );
}
